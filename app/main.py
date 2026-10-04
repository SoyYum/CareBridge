
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import get_db, init_db
from app.models import User, Document, DocumentChunk, ChatSession, ChatMessage
from app.schemas import RegisterRequest, LoginRequest, ChatRequest, ChatResponse
from app.security import hash_password, verify_password, create_token, current_user
from app.services.ingestion import extract_pdf, chunk_pages, sha256_bytes
from app.services.vector_store import get_vector_store
from app.services.rag import answer_question


# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)


app = FastAPI(
    title="CareBridge API",
    version="1.0.0",
    description="Healthcare document RAG assistant for educational use only."
)

# Register rate limiter with FastAPI
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)


@app.on_event("startup")
def startup():
    Path(settings.chroma_dir).mkdir(parents=True, exist_ok=True)
    init_db()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "CareBridge"
    }


# ---------------- AUTHENTICATION ----------------

@app.post("/auth/register")
@limiter.limit("3/minute")
def register(
    request: Request,
    payload: RegisterRequest,
    db: Session = Depends(get_db)
):
    email = payload.email.lower()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "Account already exists")

    user = User(
        email=email,
        password_hash=hash_password(payload.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "access_token": create_token(user.id),
        "token_type": "bearer"
    }


@app.post("/auth/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == payload.email.lower()
    ).first()

    if not user or not verify_password(
        payload.password,
        user.password_hash
    ):
        raise HTTPException(401, "Incorrect email or password")

    return {
        "access_token": create_token(user.id),
        "token_type": "bearer"
    }


@app.get("/me")
def me(user: User = Depends(current_user)):
    return {
        "id": user.id,
        "email": user.email
    }


# ---------------- DOCUMENT MANAGEMENT ----------------

@app.post("/documents")
async def upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(current_user)
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    data = await file.read()

    if not data:
        raise HTTPException(400, "Empty upload")

    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(
            413,
            f"PDF exceeds {settings.max_upload_mb} MB"
        )

    digest = sha256_bytes(data)

    old = db.query(Document).filter(
        Document.owner_id == user.id,
        Document.sha256 == digest
    ).first()

    if old:
        return {
            "document_id": old.id,
            "filename": old.filename,
            "chunks": old.chunk_count,
            "duplicate": True
        }

    pages, page_count = extract_pdf(data)
    chunks = chunk_pages(pages)

    if not chunks:
        raise HTTPException(
            422,
            "No extractable text. Scanned PDFs require OCR, which is not included."
        )

    doc = Document(
        owner_id=user.id,
        filename=Path(file.filename).name,
        sha256=digest,
        page_count=page_count,
        chunk_count=len(chunks)
    )

    db.add(doc)
    db.flush()

    try:
        for i, chunk in enumerate(chunks):
            db.add(
                DocumentChunk(
                    document_id=doc.id,
                    owner_id=user.id,
                    chunk_index=i,
                    page_number=chunk["page"],
                    text=chunk["text"]
                )
            )

        db.flush()

        get_vector_store().add_chunks(
            user.id,
            doc.id,
            chunks
        )

        db.commit()

    except Exception:
        db.rollback()

        try:
            get_vector_store().delete_document(user.id, doc.id)
        except Exception:
            pass

        raise

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "pages": page_count,
        "chunks": len(chunks),
        "duplicate": False
    }


@app.get("/documents")
def documents(
    db: Session = Depends(get_db),
    user: User = Depends(current_user)
):
    docs = db.query(Document).filter(
        Document.owner_id == user.id
    ).order_by(
        Document.created_at.desc()
    ).all()

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "pages": d.page_count,
            "chunks": d.chunk_count
        }
        for d in docs
    ]


@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user)
):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == user.id
    ).first()

    if not doc:
        raise HTTPException(404, "Document not found")

    get_vector_store().delete_document(user.id, doc.id)

    db.delete(doc)
    db.commit()

    return {
        "deleted": True
    }


# ---------------- CHAT ----------------

@app.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user)
):
    if payload.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == payload.session_id,
            ChatSession.owner_id == user.id
        ).first()

        if not session:
            raise HTTPException(404, "Chat session not found")

    else:
        session = ChatSession(
            owner_id=user.id,
            title=payload.question[:80]
        )

        db.add(session)
        db.commit()
        db.refresh(session)

    db.add(
        ChatMessage(
            session_id=session.id,
            role="user",
            content=payload.question
        )
    )

    db.flush()

    try:
        result = answer_question(
            db,
            user.id,
            payload.question,
            payload.language
        )

    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(503, str(exc))

    db.add(
        ChatMessage(
            session_id=session.id,
            role="assistant",
            content=result["answer"]
        )
    )

    db.commit()

    return {
        "session_id": session.id,
        "answer": result["answer"],
        "sources": result["sources"],
        "safety_notice": (
            "Educational information only; not a substitute "
            "for professional medical advice."
        )
    }


# ---------------- CHAT HISTORY ----------------

@app.get("/sessions")
def sessions(
    db: Session = Depends(get_db),
    user: User = Depends(current_user)
):
    rows = db.query(ChatSession).filter(
        ChatSession.owner_id == user.id
    ).order_by(
        ChatSession.created_at.desc()
    ).all()

    return [
        {
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at.isoformat()
        }
        for s in rows
    ]


@app.get("/sessions/{session_id}/messages")
def messages(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user)
):
    s = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.owner_id == user.id
    ).first()

    if not s:
        raise HTTPException(404, "Session not found")

    return [
        {
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat()
        }
        for m in s.messages
    ]

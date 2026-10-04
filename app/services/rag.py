
from app.config import settings
from app.models import Document
from app.services.retrieval import hybrid_search
from app.services.generation import generate_answer


def answer_question(db, owner_id, question, language="auto"):

    # Check whether the user has uploaded any documents.
    has_documents = (
        db.query(Document.id)
        .filter(Document.owner_id == owner_id)
        .first()
    )

    if not has_documents:
        return {
            "answer": (
                "You have not uploaded any documents yet. "
                "Upload a PDF to begin."
            ),
            "sources": [],
        }

    # Retrieve relevant chunks using hybrid search (dense + BM25 + RRF).
    candidates = hybrid_search(db, owner_id, question)

    if not candidates:
        return {
            "answer": (
                "I could not find sufficiently relevant information "
                "in your uploaded documents to answer this question."
            ),
            "sources": [],
        }

    # Enrich retrieved chunks with their document filenames.
    document_cache = {}

    for item in candidates:

        metadata = item.setdefault("metadata", {})
        document_id = metadata.get("document_id")

        if document_id is None:
            continue

        if document_id not in document_cache:
            document_cache[document_id] = (
                db.query(Document)
                .filter(
                    Document.id == document_id,
                    Document.owner_id == owner_id,
                )
                .first()
            )

        doc = document_cache[document_id]

        if doc:
            metadata["filename"] = doc.filename

    # CrossEncoder reranking is temporarily disabled.
    # Hybrid retrieval already returns candidates in RRF order.
    selected = candidates[:settings.top_k_final]

    if not selected:
        return {
            "answer": (
                "I could not find sufficiently relevant information "
                "in your uploaded documents to answer this question."
            ),
            "sources": [],
        }

    # Assign stable source labels before generation.
    sources = []

    for index, item in enumerate(selected, start=1):

        metadata = item.get("metadata") or {}
        item["metadata"] = metadata

        source_id = f"S{index}"
        metadata["source_id"] = source_id

        sources.append({
            "id": source_id,
            "document": metadata.get(
                "filename",
                "Uploaded document"
            ),
            "page": int(metadata.get("page", 0)),
            "excerpt": item.get("text", "")[:420],
            "score": round(
                float(
                    item.get(
                        "rrf_score",
                        item.get("score", 0.0)
                    )
                ),
                4,
            ),
        })

    # Generate an answer using the selected document excerpts.
    answer = generate_answer(
        question,
        selected,
        language,
    )

    return {
        "answer": answer,
        "sources": sources,
    }

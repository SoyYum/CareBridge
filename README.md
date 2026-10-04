# CareBridge — Healthcare Document RAG Assistant

CareBridge is an educational assistant for questions about a user's own uploaded PDF documents. It is not a medical device and must not be used for diagnosis, treatment or medication decisions.

## Included
- FastAPI API: registration, login, JWT auth, documents, chat sessions and messages.
- PostgreSQL persistence (SQLite fallback for local smoke testing).
- PDF extraction, page-aware overlapping chunking, SHA-256 duplicate detection.
- Multilingual BGE-M3 embeddings, persistent ChromaDB and owner metadata filters.
- BM25 lexical retrieval, dense retrieval and Reciprocal Rank Fusion.
- Cross-Encoder reranking.
- Local Ollama generation with conservative healthcare instructions.
- Document/page source excerpts and English/Hindi response preference.
- Retrieval evaluation: Precision@K, Recall@K, MRR and nDCG@K.
- Streamlit interface for accounts, upload, chat, sources and deletion.

## Boundaries and safety
This is a local demo implementation, not a production healthcare application. It isolates SQL records by authenticated owner and filters vector retrieval by owner metadata, but production deployment still requires independent security review, tenant-isolation tests, encrypted storage, rate limiting, audit logs, backups, secret rotation and privacy/legal review. Do not upload real patient records during development. PDFs may be outdated or incorrect. Scanned PDFs need OCR, which is not included. Evaluation needs a properly labeled dataset; sample CSV is only a schema example. No clinical validation is claimed.

## Windows setup
1. Install Python 3.11, PostgreSQL 15+, and Ollama.
2. Create a PostgreSQL database named `carebridge` and user/password matching `.env`.
3. Run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env`, especially `DATABASE_URL` and a long random `JWT_SECRET`.

4. Start the local model:

```powershell
ollama pull qwen2.5:3b
```

Ollama normally runs as a background service. If not, start `ollama serve`.

5. Terminal 1:

```powershell
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

6. Terminal 2:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend.py
```

Open http://localhost:8501.

## First-run notes
The embedding model and reranker download on first use and can require several GB of disk/RAM. If BGE-M3 is too large, set `EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` in `.env`. If changing the embedding model after indexing, rebuild the Chroma index so vector dimensions and model semantics remain consistent.

## Evaluation
The evaluator consumes a CSV with `question`, `relevant_chunk_ids`, and `retrieved_chunk_ids` columns. Chunk IDs are semicolon-separated.

```powershell
python evaluation.py sample_evaluation.csv --k 5
```

It evaluates supplied retrieval outputs only; it does not execute the live pipeline or calculate faithfulness. Do not report sample metrics as measured project performance.

## Tests
```powershell
pytest -q
```
Tests cover chunking and metric calculations only. They do not validate PostgreSQL, Chroma, model downloads, Ollama, auth end-to-end, or multi-user isolation.

## API endpoints
- `GET /health`
- `POST /auth/register`, `POST /auth/login`, `GET /me`
- `POST /documents`, `GET /documents`, `DELETE /documents/{id}`
- `POST /chat`
- `GET /sessions`, `GET /sessions/{id}/messages`

## Troubleshooting
- 401: log in again.
- Ollama unavailable: start Ollama and check `ollama list`.
- PDF has no text: likely scanned; OCR is not included.
- PostgreSQL refused: check service, database and credentials.
- Chroma dimension mismatch after model change: back up and remove `storage/chroma`, then re-upload.

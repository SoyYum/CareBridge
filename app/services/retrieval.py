
import re

from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Document, DocumentChunk
from app.services.vector_store import get_vector_store


_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "but",
    "by", "can", "could", "did", "do", "does", "for", "from", "had",
    "has", "have", "how", "i", "in", "is", "it", "its", "may", "might",
    "of", "on", "or", "should", "that", "the", "their", "this", "to",
    "was", "were", "what", "when", "where", "which", "who", "why",
    "will", "with", "would", "you", "your", "ke", "kya", "hai", "hain",
    "ka", "ki", "ko", "se", "mein", "me", "aur", "kaise", "kab",
}


def tokens(text: str) -> list[str]:
    """
    Tokenize text and remove common English and Hindi stopwords.
    """

    return [
        token
        for token in re.findall(
            r"\w+",
            (text or "").lower(),
            flags=re.UNICODE,
        )
        if token not in _STOPWORDS and len(token) > 1
    ]


def bm25_search(
    db: Session,
    owner_id: int,
    question: str,
    limit: int,
) -> list[dict]:
    """
    Perform keyword-based BM25 retrieval.

    Only searches chunks belonging to the authenticated user.
    """

    if limit <= 0:
        return []

    rows = (
        db.query(
            DocumentChunk,
            Document.filename,
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .filter(
            DocumentChunk.owner_id == owner_id,
            Document.owner_id == owner_id,
        )
        .all()
    )

    if not rows:
        return []

    query_tokens = tokens(question)

    if not query_tokens:
        return []

    corpus = [
        tokens(chunk.text)
        for chunk, _ in rows
    ]

    if not any(corpus):
        return []

    model = BM25Okapi(corpus)

    scores = model.get_scores(query_tokens)

    ranked = sorted(
        enumerate(scores),
        key=lambda pair: pair[1],
        reverse=True,
    )

    results = []

    for index, score in ranked:

        # A BM25 score <= 0 means no query terms matched.
        if score <= 0:
            continue

        chunk, filename = rows[index]

        results.append(
            {
                "id": (
                    f"{owner_id}:"
                    f"{chunk.document_id}:"
                    f"{chunk.chunk_index}"
                ),

                "text": chunk.text,

                "metadata": {
                    "owner_id": owner_id,
                    "document_id": chunk.document_id,
                    "page": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "filename": filename,
                },

                "score": float(score),
                "retrieval_method": "bm25",
            }
        )

        if len(results) >= limit:
            break

    return results


def hybrid_search(
    db: Session,
    owner_id: int,
    question: str,
):
    """
    Hybrid retrieval using:
    1. Gemini embeddings + Qdrant dense retrieval.
    2. BM25 keyword retrieval.
    3. Reciprocal Rank Fusion (RRF).

    CrossEncoder reranking is disabled for cloud deployment.
    """

    dense = get_vector_store().query(
        owner_id,
        question,
        settings.top_k_dense,
    )

    sparse = bm25_search(
        db,
        owner_id,
        question,
        settings.top_k_bm25,
    )

    best_dense = max(
        (
            float(item.get("score", 0.0))
            for item in dense
        ),
        default=0.0,
    )

    # Reject weak dense matches when BM25 finds no matching terms.
    if not sparse and best_dense < 0.48:
        return []

    merged = {}

    # Reciprocal Rank Fusion.
    for ranking in (dense, sparse):

        for rank, item in enumerate(ranking, start=1):

            key = item["id"]

            if key not in merged:

                merged[key] = {
                    **item,
                    "rrf_score": 0.0,
                }

            merged[key]["rrf_score"] += (
                1.0 / (60 + rank)
            )

    dense_scores = {
        item["id"]: float(item.get("score", 0.0))
        for item in dense
    }

    for key, item in merged.items():

        item["dense_score"] = dense_scores.get(
            key,
            0.0,
        )

    return sorted(
        merged.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )


class Reranker:
    """
    Lightweight replacement for the local CrossEncoder.

    Returns candidates in their existing RRF ranking.
    No additional model is downloaded or loaded.
    """

    def rerank(
        self,
        question: str,
        candidates: list[dict],
        limit: int,
    ) -> list[dict]:

        if not candidates or limit <= 0:
            return []

        return candidates[:limit]


_reranker = None


def get_reranker():

    global _reranker

    if _reranker is None:
        _reranker = Reranker()

    return _reranker

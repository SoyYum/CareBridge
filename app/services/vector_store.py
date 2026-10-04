from uuid import uuid5, NAMESPACE_URL

from google import genai
from google.genai import types

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from app.config import settings


class VectorStore:

    def __init__(self):

        if not settings.qdrant_url or not settings.qdrant_api_key:
            raise RuntimeError(
                "QDRANT_URL or QDRANT_API_KEY is missing."
            )

        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing."
            )

        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=60,
        )

        self.collection_name = settings.qdrant_collection

        self.embedding_client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.embedding_model = settings.gemini_embedding_model
        self.embedding_dimensions = settings.gemini_embedding_dimensions

        self._create_collection()

    def _create_collection(self):

        if not self.client.collection_exists(
            collection_name=self.collection_name
        ):

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dimensions,
                    distance=Distance.COSINE,
                ),
            )

    def _embed(self, texts, task_type):

        if not texts:
            return []

        vectors = []

        # Keep requests in manageable batches.
        batch_size = 50

        for start in range(0, len(texts), batch_size):

            batch = texts[start:start + batch_size]

            response = self.embedding_client.models.embed_content(
                model=self.embedding_model,
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=self.embedding_dimensions,
                ),
            )

            if not response.embeddings:
                raise RuntimeError(
                    "Gemini returned empty embeddings."
                )

            vectors.extend(
                embedding.values
                for embedding in response.embeddings
            )

        if len(vectors) != len(texts):
            raise RuntimeError(
                "Gemini returned an unexpected number of embeddings."
            )

        return vectors

    def _point_id(self, owner_id, document_id, chunk_index):

        identity = (
            f"carebridge:{owner_id}:"
            f"{document_id}:{chunk_index}"
        )

        return str(uuid5(NAMESPACE_URL, identity))

    def add_chunks(self, owner_id, document_id, chunks):

        if not chunks:
            return

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        vectors = self._embed(
            texts,
            task_type="RETRIEVAL_DOCUMENT",
        )

        points = []

        for index, (chunk, vector) in enumerate(
            zip(chunks, vectors)
        ):

            points.append(
                PointStruct(
                    id=self._point_id(
                        owner_id,
                        document_id,
                        index,
                    ),
                    vector=vector,
                    payload={
                        "owner_id": owner_id,
                        "document_id": document_id,
                        "chunk_index": index,
                        "page": chunk["page"],
                        "text": chunk["text"],
                    },
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )

    def query(self, owner_id, question, limit):

        if limit <= 0:
            return []

        vector = self._embed(
            [question],
            task_type="RETRIEVAL_QUERY",
        )[0]

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="owner_id",
                        match=MatchValue(value=owner_id),
                    )
                ]
            ),
            limit=limit,
            with_payload=True,
        )

        output = []

        for point in results.points:

            payload = point.payload or {}

            output.append(
                {
                    "id": str(point.id),
                    "text": payload.get("text", ""),
                    "metadata": {
                        "owner_id": payload.get("owner_id"),
                        "document_id": payload.get("document_id"),
                        "page": payload.get("page"),
                        "chunk_index": payload.get("chunk_index"),
                    },
                    "score": float(point.score),
                }
            )

        return output

    def delete_document(self, owner_id, document_id):

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="owner_id",
                        match=MatchValue(value=owner_id),
                    ),
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    ),
                ]
            ),
            wait=True,
        )


_store = None


def get_vector_store():

    global _store

    if _store is None:
        _store = VectorStore()

    return _store
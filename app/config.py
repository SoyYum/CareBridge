from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Database
    database_url: str = "sqlite:///./carebridge_dev.db"

    # Legacy local storage settings (kept for compatibility)
    chroma_dir: str = "./storage/chroma"

    # Authentication
    jwt_secret: str = "development-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 120

    # Legacy local ML settings (kept temporarily)
    embedding_model: str = "BAAI/bge-m3"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"

    # Gemini API
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    gemini_embedding_dimensions: int = 768

    # Qdrant Cloud
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection: str = "carebridge_chunks"

    # Retrieval
    top_k_dense: int = 12
    top_k_bm25: int = 12
    top_k_final: int = 5

    # Document processing
    chunk_size: int = 900
    chunk_overlap: int = 150
    max_upload_mb: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
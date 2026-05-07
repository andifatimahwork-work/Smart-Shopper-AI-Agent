import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv(encoding="utf-8-sig")


@lru_cache(maxsize=1)
def get_settings() -> dict:
    return {
        "mongo_uri": os.getenv("MONGO_CONNECTION_STRING", ""),
        "mongo_db": os.getenv("MONGO_DB_NAME", "depato_store"),
        "product_collection": os.getenv("MONGO_PRODUCT_COLLECTION", "products"),
        "common_collection": os.getenv("MONGO_COMMON_COLLECTION", "common_information"),
        "product_vector_index": os.getenv("PRODUCT_VECTOR_INDEX", "vector_index"),
        "common_vector_index": os.getenv("COMMON_VECTOR_INDEX", "common_vector_index"),
        "embedding_model": os.getenv(
            "EMBEDDING_MODEL_NAME", "sentence-transformers/all-mpnet-base-v2"
        ),
        "groq_api_key": os.getenv("GROQ_API_KEY", ""),
        "groq_model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "adk_model": os.getenv(
            "ADK_MODEL", "groq/meta-llama/llama-4-scout-17b-16e-instruct"
        ),
    }


def require_env(name: str, value: str) -> None:
    if not value:
        raise RuntimeError(
            f"{name} belum diisi. Tambahkan nilainya di file .env sebelum menjalankan app."
        )

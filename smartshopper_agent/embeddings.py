from functools import lru_cache
from typing import Iterable

from sentence_transformers import SentenceTransformer

from .settings import get_settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    settings = get_settings()
    return SentenceTransformer(settings["embedding_model"])


def embed_text(text: str) -> list[float]:
    model = get_embedding_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def embed_many(texts: Iterable[str]) -> list[list[float]]:
    model = get_embedding_model()
    return model.encode(list(texts), normalize_embeddings=True).tolist()

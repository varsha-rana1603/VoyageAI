"""
Thin wrapper around sentence-transformers. Kept as a single module so the
model is loaded once (module-level singleton) instead of once per request --
loading it per-call was one of the perf issues caught in the explorer module
rebuild.
"""
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model_name)


def embed_text(text: str) -> list[float]:
    model = get_embedding_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def profile_to_embedding_text(travel_style: str | None, budget_tier: str | None, crowd_tolerance: str | None) -> str:
    """
    Turns structured profile fields into a single string for embedding.
    Keeping this in one place means the profile side and the destination
    side (see seed/destinations_seed.py) stay in sync on phrasing --
    embeddings only compare well if both sides describe things the same way.
    """
    parts = []
    if travel_style:
        parts.append(f"{travel_style} travel style")
    if budget_tier:
        parts.append(f"{budget_tier} budget")
    if crowd_tolerance:
        parts.append(f"prefers {crowd_tolerance} crowd levels")
    return ", ".join(parts) if parts else "general travel"

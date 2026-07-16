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


from app.conversation.user_profile import UserProfile


def profile_to_embedding_text(profile: UserProfile) -> str:

    parts = []

    if profile.travel_styles:
        parts.extend(profile.travel_styles)

    if profile.terrain_preferences:
        parts.extend(profile.terrain_preferences)

    if profile.crowd_preference:
        parts.append(
            f"{profile.crowd_preference} crowd"
        )

    return ", ".join(parts)
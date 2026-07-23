from app.ml.embeddings import embed_text
from app.trip_planner.domain.accommodation import Accommodation


def generate_accommodation_embedding(
    accommodation: Accommodation,
) -> list[float]:
    if not accommodation.embedding_text:
        raise ValueError("Accommodation embedding_text is empty.")

    return embed_text(accommodation.embedding_text)
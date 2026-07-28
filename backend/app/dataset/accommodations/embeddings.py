"""
Generate vector embeddings for accommodations.

Responsibilities
----------------
✓ Generate embedding vectors
✓ Attach vectors to domain objects

Not responsible for
-------------------
✗ Persistence
✗ Metadata enrichment
✗ Price estimation
"""

from app.ml.embeddings import embed_text
from app.trip_planner.domain.accommodation import Accommodation


def embed_accommodation(
    accommodation: Accommodation,
) -> Accommodation:
    """
    Generate the embedding for one accommodation.
    """

    if not accommodation.embedding_text:
        return accommodation

    accommodation.embedding = embed_text(
        accommodation.embedding_text,
    )

    return accommodation


def embed_accommodations(
    accommodations: list[Accommodation],
) -> list[Accommodation]:
    """
    Generate embeddings for a collection of accommodations.
    """

    return [
        embed_accommodation(accommodation)
        for accommodation in accommodations
    ]
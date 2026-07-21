"""Embeds the user profile and queries PostgreSQL/pgvector for the most
semantically similar destinations."""

import logging
from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.conversation.user_profile import UserProfile
from app.ml.embeddings import embed_text, profile_to_embedding_text
from app.models.destination import Destination

logger = logging.getLogger(__name__)


class CandidateRetrievalError(Exception):
    """Raised when candidate retrieval fails in a way the caller should
    handle explicitly (e.g. return a friendly error instead of a 500)."""


@dataclass
class CandidateDestination:
    destination: Destination
    semantic_score: float
    final_score: float = 0.0
    reasons: list[str] | None = None


def retrieve_candidates(
    db: Session,
    profile: UserProfile,
    top_k: int = 100,
) -> list[CandidateDestination]:
    """Retrieves the most semantically similar destinations using pgvector
    cosine similarity.

    Raises CandidateRetrievalError on embedding or DB failure so the
    caller can decide how to surface it (retry, fallback, user-facing
    error) rather than letting a raw exception propagate.
    """

    text = profile_to_embedding_text(profile)

    try:
        user_embedding = embed_text(text)
    except Exception as exc:
        logger.error("Embedding generation failed for profile: %s", exc)
        raise CandidateRetrievalError("Failed to embed user profile") from exc

    try:
        results = (
            db.query(
                Destination,
                Destination.destination_embedding.cosine_distance(
                    user_embedding
                ).label("distance"),
            )
            .order_by("distance")
            .limit(top_k)
            .all()
        )
    except SQLAlchemyError as exc:
        logger.error("Candidate retrieval query failed: %s", exc)
        raise CandidateRetrievalError("Failed to retrieve candidate destinations") from exc

    candidates: list[CandidateDestination] = []

    for destination, distance in results:
        # Convert cosine distance into a similarity score.
        # Smaller distance = higher similarity (0 distance = 1 similarity).
        semantic_score = 1.0 - float(distance)

        candidates.append(
            CandidateDestination(
                destination=destination,
                semantic_score=semantic_score,
            )
        )

    if not candidates:
        logger.warning("Candidate retrieval returned zero results for profile")

    return candidates
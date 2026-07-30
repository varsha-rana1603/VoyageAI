"""
Confidence scoring for accommodation enrichment.
"""

from app.trip_planner.domain.accommodation import Accommodation

from .schemas import HotelSemanticFeatures


def calculate_enrichment_confidence(
    accommodation: Accommodation,
    features: HotelSemanticFeatures,
) -> float:
    """
    Estimate confidence in the semantic enrichment.

    The score combines:
    - LLM's own confidence
    - Availability of Google quality signals
    """

    confidence = features.confidence

    # Boost confidence if Google has strong evidence.
    if accommodation.review_count:
        confidence += min(
            accommodation.review_count / 10000,
            1.0,
        ) * 0.10

    if accommodation.rating:
        confidence += 0.05

    return round(
        min(confidence, 1.0),
        2,
    )
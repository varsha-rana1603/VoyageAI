"""
Accommodation metadata enrichment.

Responsibilities
----------------
✓ Batch LLM semantic enrichment
✓ Apply AI extracted features
✓ Quality scoring

Not responsible for
-------------------
✗ Pricing
✗ Embeddings
✗ Persistence
"""

from app.trip_planner.domain.accommodation import Accommodation

from .enrichment.llm_classifier import (
    enrich_hotels_with_llm,
)

from .enrichment.mapper import (
    apply_semantic_features,
)

from .enrichment.quality import (
    calculate_quality_score,
)

from .enrichment.confidence import (
    calculate_enrichment_confidence,
)

from .enrichment.amenities import enrich_amenities


def enrich_accommodations(
    accommodations: list[Accommodation],
) -> list[Accommodation]:
    """
    Enrich all accommodations using a single LLM call.
    """

    semantic_results = enrich_hotels_with_llm(
        accommodations,
    )

    for accommodation in accommodations:

        features = semantic_results.get(
            accommodation.google_place_id,
        )

        if features is None:
            continue

        apply_semantic_features(
            accommodation,
            features,
        )

        enrich_amenities(accommodation)

        accommodation.quality_score = (
            calculate_quality_score(
                accommodation,
            )
        )

        accommodation.enrichment_confidence = (
            calculate_enrichment_confidence(
                accommodation,
                features,
            )
        )

        accommodation.enrichment_source = (
            "amazon.nova-lite-v1:0"
        )

    return accommodations
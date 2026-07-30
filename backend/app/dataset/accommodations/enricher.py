"""
Accommodation metadata enrichment.
"""

from dataclasses import asdict

from .enrichment.location.geoapify_client import GeoapifyClient
from app.trip_planner.domain.accommodation import Accommodation
from app.trip_planner.domain.destination import DestinationInfo

from .enrichment.llm_classifier import enrich_hotels_with_llm
from .enrichment.mapper import apply_semantic_features
from .enrichment.quality import calculate_quality_score
from .enrichment.confidence import calculate_enrichment_confidence
from .enrichment.amenities import enrich_amenities
from .enrichment.scoring import estimate_semantic_scores
from .enrichment.embedding_text import generate_embedding

from .enrichment.location.city_center import (
    compute_city_center_distance,
)

from .enrichment.location.nearby_pois import (
    fetch_nearby_pois,
)

from .enrichment.planner_metadata import (
    build_planner_metadata,
)


def enrich_accommodations(
    accommodations: list[Accommodation],
    destination,
    geoapify: GeoapifyClient,
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

        # ---------------------------------------------------------
        # LLM Semantic Enrichment
        # ---------------------------------------------------------

        apply_semantic_features(
            accommodation,
            features,
        )

        # ---------------------------------------------------------
        # Deterministic Amenity Enrichment
        # ---------------------------------------------------------

        enrich_amenities(
            accommodation,
        )

        # print("ACCO is family friendly? : ", accommodation.family_friendly)

        # ---------------------------------------------------------
        # Location Intelligence
        # ---------------------------------------------------------

        compute_city_center_distance(
            accommodation,
            destination,
        )

        poi_counts = fetch_nearby_pois(
            accommodation,
            geoapify,
        )

        build_planner_metadata(
            accommodation,
            **asdict(poi_counts),
        )

        # ---------------------------------------------------------
        # Semantic Scores
        # ---------------------------------------------------------

        estimate_semantic_scores(
            accommodation,
        )

        # ---------------------------------------------------------
        # Embeddings
        # ---------------------------------------------------------

        generate_embedding(
            accommodation,
        )

        # ---------------------------------------------------------
        # Quality & Confidence
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Debug
        # ---------------------------------------------------------

        # print(
        #     accommodation.name,
        #     # accommodation.family_friendly,
        #     {
        #         "luxury": accommodation.luxury_score,
        #         "business": accommodation.business_score,
        #         "family": accommodation.family_score,
        #         "romantic": accommodation.romantic_score,
        #         "wellness": accommodation.wellness_score,
        #         "budget": accommodation.budget_score,
        #         "planner": accommodation.planner_metadata,
        #     },
        # )

    return accommodations
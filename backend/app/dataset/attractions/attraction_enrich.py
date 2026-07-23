"""
Enrichment of attractions pulled from Google Places API.
Deterministic, rule-based - no LLM, no external API calls here.

Popularity, importance, duration, indoor/outdoor, family friendly, tags.
"""

import math

from app.trip_planner.domain.attraction import Attraction
from app.dataset.attractions.attraction_enrichment_rules import (
    infer_indoors,
    infer_family_friendly,
    infer_tags,
)

DEFAULT_DURATIONS = {
    "museum": 180,
    "art_gallery": 120,
    "historical_landmark": 150,
    "monument": 90,
    "church": 60,
    "tourist_attraction": 90,
    "park": 120,
    "zoo": 240,
    "amusement_park": 420,
}


def estimate_visit_duration(attraction: Attraction) -> int:
    """
    Temporary heuristic. Later this value will come directly
    from the Attraction database.
    """
    return DEFAULT_DURATIONS.get(attraction.attraction_type, 120)


def compute_importance(attractions: list[Attraction]) -> None:
    """
    Ranks attractions within ONE destination by popularity_score and
    assigns a prominence tier. Destination-relative, not type-based -
    a new destination with attraction types we've never seen still
    gets sensible tiers with zero manual maintenance.

    Renamed from "importance"/"highly_recommended" deliberately:
    this describes objective prominence (how famous/rated something
    is), not personal fit. Personalized recommendation happens later,
    at planning time, using the user's profile - not here.
    """
    ranked = sorted(attractions, key=lambda a: a.popularity_score or 0, reverse=True)
    n = len(ranked)

    for i, attraction in enumerate(ranked):
        percentile = i / n
        score = attraction.popularity_score or 0

        if percentile <= 0.15 and score >= 0.75:
            attraction.importance = "must_visit"
        elif percentile <= 0.50 and score >= 0.5:
            attraction.importance = "notable"
        else:
            attraction.importance = "interest_based"


MAX_REVIEWS = 500_000


def compute_popularity(attraction: Attraction) -> float:
    # Normalized popularity score between 0 and 1.
    # Log scaling so review counts don't dominate.
    rating = attraction.rating or 0.0
    reviews = attraction.review_count or 0
    rating_score = rating / 5.0
    review_score = math.log1p(reviews) / math.log1p(MAX_REVIEWS)
    popularity = 0.6 * rating_score + 0.4 * review_score

    return round(min(popularity, 1.0), 3)


def enrich_attractions(attractions: list[Attraction]) -> list[Attraction]:
    enriched = []

    for attraction in attractions:
        attraction.popularity_score = compute_popularity(attraction)        
        attraction.estimated_visit_duration_minutes = estimate_visit_duration(
            attraction
        )
        attraction.indoor = infer_indoors(attraction)
        attraction.family_friendly = infer_family_friendly(attraction)
        attraction.tags = infer_tags(attraction)
        enriched.append(attraction)
    
    compute_importance(attractions)

    return enriched
"""
Rule-based inference for fields Google Places doesn't provide directly.
Same style as compute_importance / compute_popularity: deterministic
lookup by attraction_type, no LLM calls, no external API calls.

Deliberately return None (not a guess) when attraction_type isn't in
any known set — "unknown" is a real, useful signal downstream (e.g.
the itinerary generator can treat unknown indoor/outdoor as
weather-agnostic rather than silently assuming one or the other).
"""

from app.trip_planner.domain.attraction import Attraction

# -----------------------------
# Indoor / Outdoor
# -----------------------------

INDOOR_TYPES = {
    "museum",
    "art_gallery",
    "aquarium",
    "movie_theater",
    "shopping_mall",
    "church",
    "casino",
    "library",
}

OUTDOOR_TYPES = {
    "park",
    "national_park",
    "zoo",
    "hiking_area",
    "beach",
    "monument",
    "historical_landmark",
    "amusement_park",
    "garden",
}


def infer_indoors(attraction: Attraction) -> bool | None:
    attraction_type = attraction.attraction_type

    if attraction_type in INDOOR_TYPES:
        return True

    if attraction_type in OUTDOOR_TYPES:
        return False

    return None


# -----------------------------
# Family Friendly
# -----------------------------

FAMILY_FRIENDLY_TYPES = {
    "zoo",
    "amusement_park",
    "aquarium",
    "park",
    "museum",
    "national_park",
    "beach",
}

NOT_FAMILY_FRIENDLY_TYPES = {
    "night_club",
    "bar",
    "casino",
    "adult_entertainment",
}


def infer_family_friendly(attraction: Attraction) -> bool | None:
    attraction_type = attraction.attraction_type

    if attraction_type in FAMILY_FRIENDLY_TYPES:
        return True

    if attraction_type in NOT_FAMILY_FRIENDLY_TYPES:
        return False

    return None


# -----------------------------
# Semantic Tags
# -----------------------------
# Note: this REPLACES the raw Google `types` list that normalize_attraction
# initially stores in `tags` (enrich_attractions runs after normalize and
# overwrites it). That's intentional — raw Places types are inconsistent
# and overly granular; these are the tags trip planning logic actually
# reasons over.

RATING_TAG_THRESHOLD = 4.5
POPULARITY_TAG_THRESHOLD = 0.75


def infer_tags(attraction: Attraction) -> list[str]:
    tags: list[str] = [attraction.attraction_type]

    if attraction.rating is not None and attraction.rating >= RATING_TAG_THRESHOLD:
        tags.append("highly_rated")

    if (
        attraction.popularity_score is not None
        and attraction.popularity_score >= POPULARITY_TAG_THRESHOLD
    ):
        tags.append("popular")

    if infer_family_friendly(attraction):
        tags.append("family_friendly")

    if infer_indoors(attraction) is False:
        tags.append("outdoor")
    elif infer_indoors(attraction) is True:
        tags.append("indoor")

    return tags
"""
Enrichment of attractions pulled from Google Places API
Popularity
Importance
Duration
Ticket price
Indoor/outdoor
Family friendly
Tags
Free/Paid

"""

from app.trip_planner.domain.attraction import Attraction
import math 

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


def estimate_visit_duration(
    attraction: Attraction,
) -> int:
    """
    Temporary heuristic.

    Later this value will come directly
    from the Attraction database.
    """

    return DEFAULT_DURATIONS.get(
        attraction.attraction_type,
        120,
    )


MUST_VISIT_TYPES = {
    "historical_landmark",
    "world_heritage_site",
}

HIGHLY_RECOMMENDED_TYPES = {
    "museum",
    "monument",
    "art_gallery",
    "church",
    "national_park",
}

OPTIONAL_TYPES = {
    "shopping_mall",
    "movie_theater",
    "amusement_center",
}


def compute_importance(
    attraction: Attraction,
) -> str:
    """
    Estimate how essential an attraction is
    for experiencing the destination.

    This is destination-independent for now.
    """

    attraction_type = attraction.attraction_type

    if attraction_type in MUST_VISIT_TYPES:
        return "must_visit"

    if attraction_type in HIGHLY_RECOMMENDED_TYPES:
        return "highly_recommended"

    if attraction_type in OPTIONAL_TYPES:
        return "optional"

    return "interest_based"

MAX_REVIEWS = 500_000

def compute_popularity(attraction: Attraction) -> float:
    #Computes a normalized popularity score between 0 and 1
    #Uses log scaling so review counts don't dominate

    rating = attraction.rating or 0.0
    reviews = attraction.review_count or 0
    rating_score = rating / 5.0
    review_score = (math.log1p(reviews) / math.log1p(MAX_REVIEWS))
    popularity = (0.6 * rating_score + 0.4 * review_score)

    return round(min(popularity,1.0), 3)



def enrich_attractions(attractions: list[Attraction]) -> list[Attraction]:
    enriched = []

    for attraction in attractions:
        attraction.popularity_score = compute_popularity(attraction)
        attraction.importance = compute_importance(attraction)
        attraction.estimated_visit_duration_minutes = (estimate_visit_duration(attraction))
        attraction.indoor = inder_indoors(attraction)
        attraction.family_friendly = (infer_family_friendly(attraction))
        attraction.tags = infer_tags(attraction)
        enriched.append(attraction)
    return enriched


"""

Converts raw nearby-POI data into 0-100 category scores. Returns NEUTRAL
key names (food, shopping, culture, adventure, nature) — callers (stay
enrichment, destination enrichment) map these onto whatever field names
their own downstream ranking code expects, since stays and destinations
use different naming conventions (e.g. "food_score" vs "food_scene_score").

CATEGORY_GROUPS maps each dimension to Geoapify category strings. Verify
against Geoapify's current taxonomy before relying on them at scale:
https://apidocs.geoapify.com/docs/places/#categories
"""
from app.stay.poi_search import fetch_nearby_places

CATEGORY_GROUPS = {

    "food": [
        "catering.restaurant",
        "catering.cafe"
    ],

    "shopping": [
        "commercial.shopping_mall",
        "commercial.marketplace"
    ],

    "culture": [
        "tourism.sights",
        "entertainment.museum"
    ],

    "nature": [
        "leisure.park",
        "natural"
    ],

    "adventure": [
        "sport"
    ],

    "connectivity": [
        "public_transport"
    ]
}

SATURATION_BENCHMARKS = {
    "food": 50,
    "shopping": 8,
    "culture": 8,
    "adventure": 6,
    "nature": 6,
    "connectivity": 5,
}


import math


def _count_to_score(count: int, benchmark: int) -> float:
    """
    Converts POI count into a 0-100 score using diminishing returns.

    Example:
    1 restaurant  -> low score
    10 restaurants -> good score
    50 restaurants -> excellent score

    More places still help, but the benefit decreases.
    """

    if count <= 0:
        return 0.0

    score = (
        math.log(count + 1)
        /
        math.log(benchmark + 1)
    ) * 100


    return round(
        min(score, 100),
        2
    )


def compute_category_scores(
    lat: float,
    lon: float,
    radius_m: int = 1500,
    dimensions=None,
) -> dict:
    """
    Fetches nearby POIs across the requested dimensions in ONE API call,
    then buckets and scores them.

    `dimensions`: subset of CATEGORY_GROUPS keys to compute. Defaults to
    all of them.

    Returns: { "food": .., "shopping": .., "culture": .., ... } (neutral keys)
    """
    dims = dimensions or list(CATEGORY_GROUPS.keys())
    all_categories = [cat for key in dims for cat in CATEGORY_GROUPS[key]]

    places = fetch_nearby_places(
        lat,lon,categories=all_categories, radius_m=radius_m
    )
    scores = {}
    for key in dims:
        categories = CATEGORY_GROUPS[key]
        count = sum(
            1 for place in places
            if any(cat in place["categories"] for cat in categories)
        )
        scores[key] = _count_to_score(count, SATURATION_BENCHMARKS[key])

    return scores
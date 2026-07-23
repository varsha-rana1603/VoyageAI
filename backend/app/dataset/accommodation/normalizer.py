"""
Google Places nearby-search lodging result -> domain Accommodation.

price_tier is derived here from Google's priceLevel enum string, not left
for a later enrichment pass - unlike attraction popularity/prominence,
this is a direct one-to-one mapping with no ranking logic needed, so it
belongs in normalize alongside the rest of the field mapping.

NOTE: Google's new Places API priceLevel values are:
PRICE_LEVEL_UNSPECIFIED, PRICE_LEVEL_FREE, PRICE_LEVEL_INEXPENSIVE,
PRICE_LEVEL_MODERATE, PRICE_LEVEL_EXPENSIVE, PRICE_LEVEL_VERY_EXPENSIVE.
Worth confirming against one real hotel response before trusting this -
I haven't seen an actual lodging response from your client yet, only
inferred the enum names from Google's public docs.
"""

from app.trip_planner.domain.accommodation import Accommodation
from app.trip_planner.domain.common import Coordinates

PRICE_LEVEL_TO_TIER = {
    "PRICE_LEVEL_FREE": "budget",
    "PRICE_LEVEL_INEXPENSIVE": "budget",
    "PRICE_LEVEL_MODERATE": "mid_range",
    "PRICE_LEVEL_EXPENSIVE": "luxury",
    "PRICE_LEVEL_VERY_EXPENSIVE": "luxury",
}


def infer_price_tier(place: dict) -> str | None:
    price_level = place.get("priceLevel")
    return PRICE_LEVEL_TO_TIER.get(price_level)


def normalize_accommodation(place: dict) -> Accommodation:
    return Accommodation(
        name=place["displayName"]["text"],
        google_place_id=place["id"],
        coordinates=Coordinates(
            latitude=place["location"]["latitude"],
            longitude=place["location"]["longitude"],
        ),
        lodging_type=place.get("types", ["unknown"])[0],
        description=None,
        website=place.get("websiteUri"),
        rating=place.get("rating"),
        review_count=place.get("userRatingCount"),
        price_tier=infer_price_tier(place),
        amenities=[],  # deferred - see chat, Places doesn't reliably expose this
        pool=None,
        spa=None,
        family_friendly=None,
        business_friendly=None,
        # photo_references=[photo["name"] for photo in place.get("photos", [])],
    )
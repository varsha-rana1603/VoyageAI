"""
Normalize raw Google Places (v1 API) hotel responses into the
Accommodation domain model.

No enrichment.
No pricing.
No embeddings.
"""

from app.trip_planner.domain.accommodation import Accommodation
from app.trip_planner.domain.common import Coordinates


GOOGLE_TYPE_TO_LODGING_TYPE = {
    "hotel": "hotel",
    "hostel": "hostel",
    "motel": "motel",
    "resort_hotel": "resort",
    "guest_house": "guest_house",
    "bed_and_breakfast": "bed_and_breakfast",
    "apartment_hotel": "apartment_hotel",
    "serviced_apartment": "serviced_apartment",
    "villa": "villa",
    "lodging": "hotel",
}


def infer_lodging_type(
    google_types: list[str],
) -> str:

    for google_type in google_types:

        if google_type in GOOGLE_TYPE_TO_LODGING_TYPE:
            return GOOGLE_TYPE_TO_LODGING_TYPE[
                google_type
            ]

    return "hotel"


def normalize_accommodation(
    place: dict,
) -> Accommodation:
    """
    Normalize one Google Places v1 result.
    """

    location = place.get(
        "location",
        {},
    )

    google_types = place.get(
        "types",
        [],
    )

    return Accommodation(

        # -------------------------------------------------
        # Identity
        # -------------------------------------------------

        google_place_id=place["id"],

        # -------------------------------------------------
        # Basic Information
        # -------------------------------------------------

        name=place["displayName"]["text"],

        lodging_type=infer_lodging_type(
            google_types,
        ),

        description=None,

        website=place.get(
            "websiteUri",
        ),

        coordinates=Coordinates(
            latitude=location.get(
                "latitude"
            ),
            longitude=location.get(
                "longitude"
            ),
        ),

        # -------------------------------------------------
        # Google Signals
        # -------------------------------------------------

        rating=place.get(
            "rating",
        ),

        review_count=place.get(
            "userRatingCount",
        ),

        # -------------------------------------------------
        # Pricing
        # -------------------------------------------------

        estimated_price_per_night=None,

        currency="AED",

        pricing_source=None,

        pricing_confidence=None,

        price_tier=None,

        # -------------------------------------------------
        # Amenities
        # -------------------------------------------------

        amenities=[],

        tags=google_types,

        pool=None,

        spa=None,

        family_friendly=None,

        business_friendly=None,

        # -------------------------------------------------
        # Planner Metadata
        # -------------------------------------------------

        star_rating=None,

        best_for=[],

        distance_to_city_center_km=None,

        distance_to_nearest_metro_km=None,

        planner_metadata={},

        # -------------------------------------------------
        # AI
        # -------------------------------------------------

        embedding_text=None,
    )


def normalize_accommodations(
    places: list[dict],
) -> list[Accommodation]:
    """
    Normalize a list of Google Places results.
    """

    return [
        normalize_accommodation(place)
        for place in places
    ]
"""
Google Places raw place dict -> domain Attraction.

Lives in app.dataset (not trip_planner) because this is a build-time /
ingestion-time concern, same as destination normalization.
"""

from app.trip_planner.domain.attraction import Attraction
from app.trip_planner.domain.common import Coordinates


def normalize_attraction(place: dict) -> Attraction:

    types = place.get("types", [])

    return Attraction(
        name = place["displayName"]["text"],
        google_place_id = place["id"],
        category = types[0] if types else "unknown",
        description=None,
        coordinates=Coordinates(
            latitude = place["location"]["latitude"],
            longitude = place["location"]["longitude"],
        ),
        rating = place.get("rating"),
        review_count = place.get("userRatingCount"),
        popularity_score=None,
        importance=None,
        visit_duration_minutes=None,
        estimated_ticket_price=None,
        opening_hours=
            (
                place.get(
                    "regularOpeningHours",
                    {}
                )
                .get(
                    "weekdayDescriptions",
                    []
                )
            ),
        indoor=None,
        family_friendly=None,
        website=
            place.get("websiteUri"),
        tags=types,
        experience_tags=types,
        is_free=None,

    )
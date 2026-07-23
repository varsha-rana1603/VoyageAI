"""
Google Places raw place dict -> domain Attraction.

Lives in app.dataset (not trip_planner) because this is a build-time /
ingestion-time concern, same as destination normalization.
"""

from app.trip_planner.domain.attraction import Attraction
from app.trip_planner.domain.common import Coordinates


def normalize_attraction(place: dict) -> Attraction:
    return Attraction(
        name=place["displayName"]["text"],
        google_place_id=place["id"],
        attraction_type=place.get("types", ["unknown"])[0],
        description=None,
        coordinates=Coordinates(
            latitude=place["location"]["latitude"],
            longitude=place["location"]["longitude"],
        ),
        rating=place.get("rating"),
        review_count=place.get("userRatingCount"),
        popularity_score=None,
        importance=None,
        estimated_visit_duration_minutes=None,
        estimated_ticket_price=None,
        opening_hours=(
            place.get("regularOpeningHours", {}).get("weekdayDescriptions", [])
        ),
        indoor=None,
        family_friendly=None,
        website=place.get("websiteUri"),
        # photo_references=[photo["name"] for photo in place.get("photos", [])],
        tags=place.get("types", []),
        is_free=None,
    )
from app.trip_planner.domain.accommodation import Accommodation


def enrich_amenities(accommodation: Accommodation) -> None:
    """
    Populate deterministic amenity fields from Google Place types.
    """

    tags = set(tag.lower() for tag in accommodation.tags)

    accommodation.pool = bool(
        {"swimming_pool", "pool"} & tags
    )

    accommodation.spa = bool(
        {"spa", "massage_spa", "wellness_center"} & tags
    )

    accommodation.business_friendly = bool(
        {
            "business_center",
            "conference_center",
            "convention_center",
            "meeting_room",
            "banquet_hall",
            "event_venue",
        }
        & tags
    )

    # Conservative heuristic.
    accommodation.family_friendly = (
        accommodation.pool
        or accommodation.hotel_category == "resort"
    )
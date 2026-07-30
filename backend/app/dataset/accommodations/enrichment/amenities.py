from app.trip_planner.domain.accommodation import Accommodation


def enrich_amenities(accommodation: Accommodation) -> None:
    """
    Populate deterministic amenity fields from Google Place types
    and existing semantic information.
    """

    tags = {
        tag.lower()
        for tag in accommodation.tags
    }

    amenities = set(accommodation.amenities)

    # ---------------------------------------------------------
    # Pool
    # ---------------------------------------------------------

    if accommodation.pool is None:
        accommodation.pool = bool(
            {"pool", "swimming_pool"} & tags
        )

    if accommodation.pool:
        amenities.add("pool")

    # ---------------------------------------------------------
    # Spa
    # ---------------------------------------------------------

    if accommodation.spa is None:
        accommodation.spa = bool(
            {
                "spa",
                "massage_spa",
                "wellness_center",
            } & tags
        )

    if accommodation.spa:
        amenities.add("spa")

    # ---------------------------------------------------------
    # Business
    # ---------------------------------------------------------

    if accommodation.business_friendly is None:
        accommodation.business_friendly = bool(
            {
                "business_center",
                "conference_center",
                "convention_center",
                "meeting_room",
                "banquet_hall",
                "event_venue",
            } & tags
        )

    if accommodation.business_friendly:
        amenities.add("business_center")

    # ---------------------------------------------------------
    # Family
    # ---------------------------------------------------------

    accommodation.family_friendly = (
        accommodation.pool
        or accommodation.hotel_category == "resort"
    )

    # ---------------------------------------------------------
    # Copy useful Google place types
    # ---------------------------------------------------------

    TAG_TO_AMENITY = {
        "restaurant": "restaurant",
        "gym": "gym",
        "fitness_center": "gym",
        "bar": "bar",
        "cafe": "cafe",
        "beach": "beach_access",
        "resort_hotel": "resort",
        "extended_stay_hotel": "extended_stay",
        "wedding_venue": "wedding_venue",
        "event_venue": "event_space",
    }

    for tag in tags:
        amenity = TAG_TO_AMENITY.get(tag)
        if amenity:
            amenities.add(amenity)

    accommodation.amenities = sorted(amenities)
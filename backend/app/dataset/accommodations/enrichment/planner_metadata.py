from app.trip_planner.domain.accommodation import Accommodation


def _shopping_level(count: int) -> str:
    if count >= 5:
        return "excellent"
    if count >= 2:
        return "good"
    return "limited"


def _nightlife_level(count: int) -> str:
    if count >= 8:
        return "high"
    if count >= 3:
        return "medium"
    return "low"


def _metro_level(count: int) -> str:
    if count >= 2:
        return "excellent"
    if count == 1:
        return "good"
    return "poor"


def _walkability(
    restaurants: int,
    cafes: int,
    shopping: int,
    parks: int,
) -> str:

    total = (
        restaurants
        + cafes
        + shopping
        + parks
    )

    if total >= 40:
        return "excellent"

    if total >= 20:
        return "high"

    if total >= 10:
        return "medium"

    return "low"


def build_planner_metadata(
    accommodation: Accommodation,
    *,
    restaurants: int,
    cafes: int,
    shopping: int,
    bars: int,
    parks: int,
    beaches: int,
    mountains: int,
    forests: int,
    metro: int,
) -> Accommodation:
    """
    Populate planner metadata from nearby POI counts.
    """

    accommodation.planner_metadata = {

        "walkability": _walkability(
            restaurants,
            cafes,
            shopping,
            parks,
        ),

        "metro_access": _metro_level(
            metro,
        ),

        "shopping": _shopping_level(
            shopping,
        ),

        "nightlife": _nightlife_level(
            bars,
        ),

        "waterfront": beaches > 0,

        # Raw counts (useful later)
        "poi_counts": {
            "restaurants": restaurants,
            "cafes": cafes,
            "shopping": shopping,
            "bars": bars,
            "parks": parks,
            "beaches": beaches,
            "mountains": mountains,
            "forests": forests,
            "metro": metro,
        },

        "poi_density": (
            restaurants
            + cafes
            + shopping
            + bars
            + parks
            + beaches
            + mountains 
            + forests
            + metro
        ),
    }

    return accommodation
from dataclasses import dataclass

from .geoapify_client import GeoapifyClient

from app.trip_planner.domain.accommodation import Accommodation


SEARCH_RADIUS_METERS = 1000


ALL_CATEGORIES = [

    # Food
    "catering.restaurant",
    "catering.cafe",

    # Nightlife
    "catering.bar",
    "catering.pub",

    # Shopping
    "commercial.shopping_mall",
    "commercial.marketplace",

    # Nature
    "leisure.park",
    "natural.forest",
    "natural.mountain",

    # Transport
    "public_transport",
]

@dataclass
class NearbyPOICounts:

    restaurants: int = 0
    cafes: int = 0
    shopping: int = 0
    bars: int = 0
    parks: int = 0
    beaches: int = 0
    mountains: int = 0
    forests: int = 0
    metro: int = 0


def fetch_nearby_pois(
    accommodation: Accommodation,
    client: GeoapifyClient,
) -> NearbyPOICounts:

    results = client.nearby_places(
        latitude=accommodation.coordinates.latitude,
        longitude=accommodation.coordinates.longitude,
        radius=SEARCH_RADIUS_METERS,
        categories=ALL_CATEGORIES,
    )

    counts = NearbyPOICounts()

    for feature in results:

        categories = set(
            feature["properties"].get(
                "categories",
                [],
            )
        )


        # Food
        if any(
            c.startswith("catering.restaurant")
            for c in categories
        ):
            counts.restaurants += 1


        if any(
            c.startswith("catering.cafe")
            for c in categories
        ):
            counts.cafes += 1


        if any(
            c.startswith("catering.bar")
            or c.startswith("catering.pub")
            for c in categories
        ):
            counts.bars += 1


        # Shopping
        if any(
            c.startswith("commercial.shopping")
            or c.startswith("commercial.marketplace")
            for c in categories
        ):
            counts.shopping += 1


        # Nature
        if any(
            c.startswith("leisure.park")
            for c in categories
        ):
            counts.parks += 1


        if any(
            "forest" in c
            for c in categories
        ):
            counts.forests += 1


        if any(
            "mountain" in c
            or "peak" in c
            for c in categories
        ):
            counts.mountains += 1


        # Transport
        if any(
            c.startswith("public_transport")
            for c in categories
        ):
            counts.metro += 1

    return counts
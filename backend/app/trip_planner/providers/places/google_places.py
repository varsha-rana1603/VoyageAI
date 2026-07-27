# given a destination, return attractions
#
# Anti-corruption layer:
# This module knows nothing about the database or domain models.
# It only translates VoyageAI search intent into Google Places calls.

from app.clients.places_client import search_destination_attractions

from app.conversation.user_profile import UserProfile
from app.trip_planner.providers.interests.search_interests import (
    INTEREST_SEARCHES,
)


def generate_search_queries(
    user_profile: UserProfile,
) -> list[str]:
    queries = ["tourist attractions"]

    for interest in user_profile.exploration_interests:
        queries.extend(
            INTEREST_SEARCHES.get(
                interest.lower(),
                [],
            )
        )

    # Preserve order while removing duplicates
    return list(dict.fromkeys(queries))


def deduplicate_places(
    places: list[dict],
) -> list[dict]:
    unique = {}

    for place in places:
        place_id = place.get("id")

        if place_id:
            unique[place_id] = place

    return list(unique.values())


def get_destination_attractions(
    *,
    latitude: float,
    longitude: float,
    search_queries: list[str],
    radius_meters: int = 20_000,
    limit_per_query: int = 10,
) -> list[dict]:

    print("Discovering attractions...")

    all_places: list[dict] = []

    for query in search_queries:

        print(f"Searching: {query}")

        places = search_destination_attractions(
            query=query,
            latitude=latitude,
            longitude=longitude,
            radius_meters=radius_meters,
            limit=limit_per_query,
        )

        print(f"  -> {len(places)} results")

        all_places.extend(places)

    unique_places = deduplicate_places(all_places)

    print(
        f"\nDiscovered {len(unique_places)} unique attractions."
    )

    return unique_places
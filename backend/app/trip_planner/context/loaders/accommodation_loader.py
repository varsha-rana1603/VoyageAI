"""
Given a destination, return nearby lodging (raw Places dicts).

Anti-corruption layer, same role as get_destination_attractions -
callers (ingestion) never touch places_client or raw Google Places
response shapes directly. Deliberately does NOT normalize - that's
dataset/accommodations/normalize.py's job, kept separate so the
providers layer only ever knows about Google's shape, never the
domain's.
"""

from app.clients.places_client import search_destination_accommodations


def get_destination_accommodations(
    destination: str,
    country: str,
    limit: int = 20,
) -> list[dict]:
    print("getting accommodations...")
    query = f"places to stay in {destination}, {country}"

    accommodations = search_destination_accommodations(
        query=query,
        limit=limit,
    )

    print("Accommodations: ", accommodations)
    return accommodations
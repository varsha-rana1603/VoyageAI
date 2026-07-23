#given a destination, return attractions

#Anti-corruption layer as it doesn't know anything about VoyageAI 
#Prevents external API models from leaking into your domain models

from app.clients.places_client import (
    search_destination_attractions,
)


def get_destination_attractions(
    destination: str,
    country: str,
    limit: int = 30,
) -> list[dict]:
    print("getting attractions...")
    query = f"tourist attractions in {destination}, {country}"

    attractions = search_destination_attractions(
        query=query,
        limit=limit,
    )

    print("Attractions: ", attractions)
    return attractions
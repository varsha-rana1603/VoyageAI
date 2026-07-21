from dataclasses import dataclass

from app.clients.places_client import (
    search_destination,
    get_place_details,
)


@dataclass
class VerifiedDestination:

    name: str

    country: str

    category: str

    google_place_id: str

    latitude: float

    longitude: float

def verify_destination(
    destination_name: str,
    country: str,
    category: str,
) -> VerifiedDestination | None:
    """
    Verifies a destination using Google Places.

    Returns None if the destination cannot be verified.
    """

    query = f"{destination_name}, {country}"

    try:

        search = search_destination(query)

        details = get_place_details(
            search["id"]
        )

    except Exception:

        return None

    return VerifiedDestination(

        name=details["name"],

        country=details["country"],

        category=category,

        google_place_id=details[
            "google_place_id"
        ],

        latitude=details["latitude"],

        longitude=details["longitude"],
    )

from app.dataset.schemas import CountryDestinations


def verify_country(
    country_data: CountryDestinations,
) -> list[VerifiedDestination]:

    verified = []

    for destination in country_data.destinations:

        print(
            f"Verifying {destination.name}"
        )

        result = verify_destination(

            destination_name=destination.name,

            country=country_data.country,

            category=destination.category,
        )

        if result:

            verified.append(result)

    return verified

def verify_dataset(
    countries: list[CountryDestinations],
) -> list[VerifiedDestination]:

    verified = []

    for country in countries:

        verified.extend(

            verify_country(
                country
            )

        )

    return verified
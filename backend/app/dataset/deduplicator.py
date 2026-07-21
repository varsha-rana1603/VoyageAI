from app.dataset.verifier import VerifiedDestination


def deduplicate_destinations(
    destinations: list[VerifiedDestination],
) -> list[VerifiedDestination]:
    """
    Removes duplicate destinations using Google Place ID.
    """

    unique: dict[str, VerifiedDestination] = {}

    for destination in destinations:

        unique[destination.google_place_id] = destination

    return list(unique.values())

from collections import defaultdict

from app.dataset.verifier import VerifiedDestination


def find_duplicates(
    destinations: list[VerifiedDestination],
) -> dict[str, list[VerifiedDestination]]:

    grouped = defaultdict(list)

    for destination in destinations:

        grouped[destination.google_place_id].append(
            destination
        )

    return {
        place_id: values
        for place_id, values in grouped.items()
        if len(values) > 1
    }
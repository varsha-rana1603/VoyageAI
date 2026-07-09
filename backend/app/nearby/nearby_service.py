from app.nearby.google_places_provider import fetch_sights_for_destination
from app.nearby.ranking import rank_sights
from app.nearby.explanation import explain_sights
from app.nearby.relationship import (
    link_sights_to_stays,
    link_stays_to_sights
)


def get_nearby_places(
    destination_lat: float,
    destination_lon: float,
    category_weights: dict,
    recommended_stays: list,
):
    """
    Complete destination exploration pipeline.

    Flow:

    Google Places
        |
        |
    Normalize sights
        |
        |
    Rank sights
        |
        |
    Generate explanations
        |
        |
    Connect stays <-> sights
    """

    # 1. Fetch destination sights

    sights = fetch_sights_for_destination(
        lat=destination_lat,
        lon=destination_lon
    )


    # 2. Rank according to user preferences

    ranked_sights = rank_sights(
        sights=sights,
        category_weights=category_weights,
        destination_lat=destination_lat,
        destination_lon=destination_lon
    )


    # 3. Add personalised explanations

    explained_sights = explain_sights(
        ranked_sights,
        category_weights
    )


    # 4. Connect sights with recommended stays

    explained_sights = link_sights_to_stays(
        sights=explained_sights,
        stays=recommended_stays
    )


    # 5. Connect stays with nearby sights

    recommended_stays = link_stays_to_sights(
        stays=recommended_stays,
        sights=explained_sights
    )


    return {

        "sights": explained_sights,

        "stays": recommended_stays

    }
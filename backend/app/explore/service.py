from app.stay.recommender import get_stay_recommendations

from app.nearby.sight_cache import get_sights_for_destination
from app.nearby.ranking import rank_sights
from app.nearby.explanation import explain_sights
from app.nearby.relationship import (
    link_sights_to_stays,
    link_stays_to_sights
)

from app.nearby.preference_engine import compute_category_weights



def get_destination_explore(
    destination_name,
    lat,
    lon,
    travel_style,
    budget,
    crowd_tolerance,
    terrain,
    free_text
):

    # -------------------------
    # 1. Fetch recommended stays
    # -------------------------

    stays = get_stay_recommendations(
        destination_name=destination_name,
        travel_style=travel_style,
        budget=budget,
        crowd_tolerance=crowd_tolerance,
        terrain=terrain,
        free_text=free_text
    )


    # -------------------------
    # 2. Fetch destination sights
    # -------------------------

    sights = get_sights_for_destination(
        destination_name,
        lat,
        lon
    )


    # -------------------------
    # 3. Personal preference weights
    # -------------------------

    category_weights = compute_category_weights(
        travel_style=travel_style,
        budget=budget,
        crowd_tolerance=crowd_tolerance,
        terrain=terrain,
        free_text=free_text
    )


    # -------------------------
    # 4. Rank sights
    # -------------------------

    ranked_sights = rank_sights(
        sights,
        category_weights,
        lat,
        lon
    )


    explained_sights = explain_sights(
        ranked_sights,
        category_weights
    )


    # -------------------------
    # 5. Create relationships
    # -------------------------

    explained_sights = link_sights_to_stays(
        explained_sights,
        stays
    )


    stays = link_stays_to_sights(
        stays,
        explained_sights
    )


    return {

        "destination": destination_name,

        "stays": stays,

        "sights": explained_sights

    }
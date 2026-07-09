from app.stay.poi_scoring import compute_category_scores


def enrich_stays_with_surroundings(
        stays: list,
        surroundings: dict
):
    """
    Adds destination-level POI scores to every stay.
    surroundings is fetched ONCE per destination.
    """

    for stay in stays:

        stay.update({

            "food_score": surroundings.get(
                "food",
                50
            ),

            "shopping_score": surroundings.get(
                "shopping",
                50
            ),

            "culture_score": surroundings.get(
                "culture",
                50
            ),

            "nature_score": surroundings.get(
                "nature",
                50
            ),

            "adventure_score": surroundings.get(
                "adventure",
                50
            ),

            "connectivity_score": surroundings.get(
                "connectivity",
                50
            )
        })

    return stays
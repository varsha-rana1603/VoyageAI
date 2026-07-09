# app/stay/stay_enrichment.py

from typing import Dict
from concurrent.futures import ThreadPoolExecutor


def budget_score(stay_type: str) -> int:
    mapping = {
        "hostel": 90,
        "guest house": 80,
        "homestay": 75,
        "hotel": 60,
        "resort": 40,
        "apartment": 70,
    }

    return mapping.get(
        stay_type.lower(),
        50
    )


def distance_score(distance: float) -> int:
    """
    Convert distance from city center into score.
    """

    if distance <= 1:
        return 100

    if distance <= 3:
        return 90

    if distance <= 5:
        return 80

    if distance <= 8:
        return 70

    return 60



def enrich_stay(
        stay: Dict,
        surroundings: Dict
) -> Dict:

    # Budget preference score
    stay["budget_score"] = budget_score(
        stay.get("type", "")
    )


    # Distance score
    stay["distance_score"] = distance_score(
        stay.get(
            "distance_from_center",
            10
        )
    )


    # Destination level POI scores
    stay["food_score"] = surroundings.get(
        "food",
        50
    )

    stay["shopping_score"] = surroundings.get(
        "shopping",
        50
    )

    stay["culture_score"] = surroundings.get(
        "culture",
        50
    )

    stay["nature_score"] = surroundings.get(
        "nature",
        50
    )

    stay["adventure_score"] = surroundings.get(
        "adventure",
        50
    )

    stay["connectivity_score"] = surroundings.get(
        "connectivity",
        50
    )


    return stay





def enrich_stays(
        stays,
        surroundings
):
    """
    Enrich multiple stays.

    surroundings:
        {
            "food":80,
            "shopping":70,
            "culture":90,
            "nature":60,
            "adventure":50,
            "connectivity":90
        }

    is calculated once before this function.
    """


    with ThreadPoolExecutor(
        max_workers=10
    ) as executor:


        enriched = list(
            executor.map(
                lambda stay:
                    enrich_stay(
                        stay,
                        surroundings
                    ),
                stays
            )
        )


    return enriched
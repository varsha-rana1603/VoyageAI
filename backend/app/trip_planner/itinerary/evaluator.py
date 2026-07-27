"""
app/trip_planner/itinerary/evaluator.py

Evaluates one search transition.

Input:
    FeatureVector

Output:
    float score

Higher score = better future itinerary path.

This module does not search.
It does not know about beam search.

It only answers:

"How good is taking this action?"
"""

from __future__ import annotations

from .models import FeatureVector


# ==========================================================
# Linear weights
# ==========================================================

WEIGHTS = {

    # ------------------------------------------------------
    # Attraction desirability
    # ------------------------------------------------------

    "ranking_score": 0.45,

    "rating": 0.15,

    "popularity": 0.08,


    # ------------------------------------------------------
    # Route efficiency
    # ------------------------------------------------------

    "travel_minutes": -0.12,

    "travel_distance_km": -0.05,

    "walking_minutes": -0.04,


    # ------------------------------------------------------
    # Experience diversity
    # ------------------------------------------------------

    "category_repeat": -0.20,


    # ------------------------------------------------------
    # User comfort
    # ------------------------------------------------------

    "remaining_energy": 0.15,


    # ------------------------------------------------------
    # Day utilization
    # ------------------------------------------------------

    "attraction_ratio": 0.05,

}



# ==========================================================
# Main API
# ==========================================================


def evaluate(
    features: FeatureVector,
) -> float:


    score = 0.0


    # base model

    for key,value in features.values.items():

        score += (
            WEIGHTS.get(key,0)
            *
            value
        )


    # domain adjustments

    score += diversity_bonus(features)

    score += category_fatigue(features)

    score += travel_penalty(features)

    score += energy_adjustment(features)

    score += meal_adjustment(features)

    score += end_day_adjustment(features)


    return score



# ==========================================================
# Diversity
# ==========================================================


def diversity_bonus(
    features
):

    repeat = features.values.get(
        "category_repeat",
        0
    )


    if repeat == 0:
        return 0.15


    if repeat == 1:
        return 0.05


    return 0



# ==========================================================
# Category fatigue
# ==========================================================


def category_fatigue(
    features
):

    score = 0


    museum_repeat = features.values.get(
        "museum_repeat",
        0
    )

    castle_repeat = features.values.get(
        "castle_repeat",
        0
    )


    # museum overload

    if museum_repeat >= 3:
        score -= 0.25


    elif museum_repeat == 2:
        score -= 0.10



    # castle overload

    if castle_repeat >= 3:
        score -= 0.25


    elif castle_repeat == 2:
        score -= 0.10


    return score



# ==========================================================
# Travel efficiency
# ==========================================================


def travel_penalty(
    features
):

    minutes = features.values.get(
        "travel_minutes",
        0
    )


    if minutes > 60:
        return -0.30


    if minutes > 35:
        return -0.15


    return 0



# ==========================================================
# Energy
# ==========================================================


def energy_adjustment(
    features
):

    energy = features.values.get(
        "remaining_energy",
        1
    )


    if energy > 0.8:
        return 0.10


    if energy < 0.3:
        return -0.20


    return 0



# ==========================================================
# Meals
# ==========================================================


def meal_adjustment(
    features
):

    score = 0


    if features.values.get(
        "is_lunch",
        0
    ):
        score += 0.15


    if features.values.get(
        "is_dinner",
        0
    ):
        score += 0.15


    return score



# ==========================================================
# End day decision
# ==========================================================


def end_day_adjustment(
    features
):

    if not features.values.get(
        "is_end_day",
        0
    ):
        return 0


    utilization = features.values.get(
        "attraction_ratio",
        0
    )


    # finishing after a productive day

    if utilization > 0.8:
        return 0.35


    if utilization > 0.5:
        return 0.10


    # don't reward wasting a day

    return -0.25
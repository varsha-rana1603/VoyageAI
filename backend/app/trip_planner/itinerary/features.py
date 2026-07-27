"""
app/trip_planner/itinerary/features.py

Extracts numerical features describing a search transition.

This module NEVER decides whether a move is good.

It simply converts

    parent_state
    + move
    + resulting_state

into a numerical FeatureVector.

Later the evaluator may be replaced by

    LightGBM
    XGBoost
    Neural Networks

without changing anything here.
"""

from __future__ import annotations

from .constraints import ConstraintProfile
from .models import (
    FeatureVector,
    Move,
    MoveType,
    PlannerState,
)
from .route import RouteEstimate

from ..attractions.models import RankedAttraction


# ============================================================
# Public API
# ============================================================


def extract_features(
    parent_state: PlannerState,
    resulting_state: PlannerState,
    move: Move,
    attraction: RankedAttraction | None,
    route: RouteEstimate | None,
    profile: ConstraintProfile,
) -> FeatureVector:

    values: dict[str, float] = {}

    values.update(
        _attraction_features(attraction)
    )

    values.update(
        _travel_features(route)
    )

    values.update(
        _category_features(
            parent_state,
            attraction,
        )
    )

    values.update(
        _time_features(
            resulting_state,
        )
    )

    values.update(
        _constraint_features(
            resulting_state,
            profile,
        )
    )

    values.update(
        _meal_features(
            resulting_state,
        )
    )

    values.update(
        _progress_features(
            resulting_state,
        )
    )

    values.update(
        _move_features(move)
    )

    values.update(
        _value_features(attraction)
    )

    return FeatureVector(values=values)


# ============================================================
# Attraction
# ============================================================


def _attraction_features(
    attraction: RankedAttraction | None,
) -> dict[str, float]:

    if attraction is None:

        return {

            "ranking_score": 0.0,

            "rating": 0.0,

            "popularity": 0.0,

            "visit_duration_minutes": 0.0,

        }

    return {

        "ranking_score":
            attraction.score,

        "rating":
            (
                attraction.rating / 5
                if attraction.rating is not None
                else 0.0
            ),

        "popularity":
            (
                attraction.popularity_score
                if attraction.popularity_score is not None
                else 0.0
            ),

        "visit_duration_minutes":
            attraction.visit_duration_minutes,

    }


# ============================================================
# Travel
# ============================================================


def _travel_features(
    route: RouteEstimate | None,
) -> dict[str, float]:

    if route is None:

        return {

            "travel_minutes": 0.0,

            "travel_distance_km": 0.0,

            "walking_minutes": 0.0,

            "is_walk": 0.0,

            "is_metro": 0.0,

            "is_taxi": 0.0,

        }

    return {

        "travel_minutes":
            route.duration_minutes,

        "travel_distance_km":
            route.distance_km,

        "walking_minutes":
            (
                route.duration_minutes
                if route.mode.value == "walk"
                else 0.0
            ),

        "is_walk":
            float(route.mode.value == "walk"),

        "is_metro":
            float(route.mode.value == "metro"),

        "is_taxi":
            float(route.mode.value == "taxi"),

    }


# ============================================================
# Category diversity
# ============================================================


def _category_features(
    state: PlannerState,
    attraction: RankedAttraction | None,
) -> dict[str, float]:

    if attraction is None:

        return {

            "category_repeat": 0.0,

            "museum_repeat": 0.0,

            "castle_repeat": 0.0,

            "park_repeat": 0.0,

        }

    category = attraction.category.lower()

    count = state.category_counts_today.get(
        category,
        0,
    )

    return {

        "category_repeat":
            float(count),

        "museum_repeat":
            float(
                category == "museum"
            ) * count,

        "castle_repeat":
            float(
                category == "castle"
            ) * count,

        "park_repeat":
            float(
                category == "park"
            ) * count,

    }


# ============================================================
# Time
# ============================================================


def _time_features(
    state: PlannerState,
) -> dict[str, float]:

    hour = (
        state.current_time.hour
        + state.current_time.minute / 60
    )

    return {

        "hour_of_day":
            hour,

        "remaining_energy":
            state.energy,

    }


# ============================================================
# Constraint utilization
# ============================================================


def _constraint_features(
    state: PlannerState,
    profile: ConstraintProfile,
) -> dict[str, float]:

    return {

        "walking_ratio":

            state.walking_minutes_today
            / profile.max_walking_minutes_per_day,

        "attraction_ratio":

            state.attraction_minutes_today
            / profile.max_attraction_minutes_per_day,

    }


# ============================================================
# Meals
# ============================================================


def _meal_features(
    state: PlannerState,
) -> dict[str, float]:

    return {

        "lunch_taken":

            float(
                "lunch"
                in state.meals_taken_today
            ),

        "dinner_taken":

            float(
                "dinner"
                in state.meals_taken_today
            ),

    }


# ============================================================
# Progress
# ============================================================


def _progress_features(
    state: PlannerState,
) -> dict[str, float]:

    return {

        "visited_count":

            float(
                len(
                    state.visited_attraction_ids
                )
            ),

        "current_day":

            float(
                state.current_day
            ),

    }


# ============================================================
# Move
# ============================================================


def _move_features(
    move: Move,
) -> dict[str, float]:

    return {

        "is_visit":

            float(
                move.move_type
                == MoveType.VISIT_ATTRACTION
            ),

        "is_lunch":

            float(
                move.move_type
                == MoveType.TAKE_LUNCH
            ),

        "is_dinner":

            float(
                move.move_type
                == MoveType.TAKE_DINNER
            ),

        "is_end_day":

            float(
                move.move_type
                == MoveType.END_DAY
            ),

    }

def _value_features(
    attraction,
):

    if attraction is None:
        return {}

    return {

        "value_density":
            attraction.score /
            max(
                attraction.visit_duration_minutes,
                1
            )

    }
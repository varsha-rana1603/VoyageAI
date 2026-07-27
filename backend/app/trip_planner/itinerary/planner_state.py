"""
app/trip_planner/itinerary/planner_state.py

Pure state transition engine.

state + move -> new state

No scoring.
No legality.
No move generation.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta

from .models import (
    Location,
    Move,
    MoveType,
    PlannerState,
    Stop,
    DayPlan,
)

from .route import estimate_route

from ..attractions.models import RankedAttraction


DEFAULT_VISIT_DURATION = 120

LUNCH_DURATION = 60

DINNER_DURATION = 75



def apply_move(
    state: PlannerState,
    move: Move,
    attractions: dict[int, RankedAttraction],
) -> PlannerState:


    if move.move_type == MoveType.VISIT_ATTRACTION:

        return _visit_attraction(
            state,
            move,
            attractions,
        )


    if move.move_type == MoveType.TAKE_LUNCH:

        return _take_meal(
            state,
            "lunch",
            LUNCH_DURATION,
        )


    if move.move_type == MoveType.TAKE_DINNER:

        return _take_meal(
            state,
            "dinner",
            DINNER_DURATION,
        )


    if move.move_type == MoveType.END_DAY:

        return _end_day(state)


    if move.move_type == MoveType.END_TRIP:

        return replace(
            state,
            current_day=state.current_day + 999,
        )


    return state



# ==========================================================
# Attraction
# ==========================================================


def _visit_attraction(
    state,
    move,
    attractions,
):

    attraction = attractions[
        move.attraction_id
    ]


    destination = Location(

        latitude=attraction.latitude,

        longitude=attraction.longitude,

        attraction_id=attraction.attraction_id,

        label=attraction.name,

    )


    route = estimate_route(
        state.current_location,
        destination,
    )


    visit_minutes = (
        attraction.visit_duration_minutes
        or DEFAULT_VISIT_DURATION
    )


    arrival = _add_minutes(
        state.current_time,
        route.duration_minutes,
    )


    departure = _add_minutes(
        arrival,
        visit_minutes,
    )


    stop = Stop(

        move_type=MoveType.VISIT_ATTRACTION,

        attraction_id=attraction.attraction_id,

        name=attraction.name,

        arrival_time=arrival,

        departure_time=departure,

        travel_minutes_from_previous=
            route.duration_minutes,

        travel_mode=
            route.mode.value,

    )


    category = attraction.category.lower()


    # ------------------------------
    # Daily category memory
    # ------------------------------

    category_counts = {
        **state.category_counts_today
    }

    category_counts[category] = (
        category_counts.get(category, 0)
        + 1
    )


    # ------------------------------
    # Whole trip category memory
    # ------------------------------

    total_categories = {
        **state.category_counts_total
    }

    total_categories[category] = (
        total_categories.get(category, 0)
        + 1
    )


    return replace(

        state,

        current_time=departure,

        current_location=destination,


        visited_attraction_ids=
            state.visited_attraction_ids
            |
            {
                attraction.attraction_id
            },


        day_stops=
            state.day_stops
            +
            (stop,),


        walking_minutes_today=
            state.walking_minutes_today
            +
            (
                route.duration_minutes
                if route.mode.value == "walk"
                else 0
            ),


        travel_minutes_today=
            state.travel_minutes_today
            +
            route.duration_minutes,


        attraction_minutes_today=
            state.attraction_minutes_today
            +
            visit_minutes,


        category_counts_today=
            category_counts,


        # NEW:
        # remembers entire trip distribution
        category_counts_total=
            total_categories,


        energy=
            max(
                0,
                state.energy
                -
                _energy_cost(
                    route.duration_minutes,
                    visit_minutes,
                )
            ),

    )



# ==========================================================
# Meals
# ==========================================================


def _take_meal(
    state,
    meal,
    duration,
):


    move_type = (
        MoveType.TAKE_LUNCH
        if meal == "lunch"
        else MoveType.TAKE_DINNER
    )


    stop = Stop(

        move_type=move_type,

        attraction_id=None,

        name=meal.title(),

        arrival_time=state.current_time,

        departure_time=
            _add_minutes(
                state.current_time,
                duration,
            ),

    )


    return replace(

        state,

        current_time=
            stop.departure_time,


        day_stops=
            state.day_stops
            +
            (stop,),


        meals_taken_today=
            state.meals_taken_today
            |
            {meal},

    )



# ==========================================================
# End day
# ==========================================================


def _end_day(
    state,
):


    day_plan = DayPlan(

        day_number=
            state.current_day,

        stops=
            state.day_stops,

        walking_minutes=
            state.walking_minutes_today,

        travel_minutes=
            state.travel_minutes_today,

    )


    return replace(

        state,

        current_day=
            state.current_day + 1,


        current_time=
            datetime.strptime(
                "09:00",
                "%H:%M"
            ).time(),


        committed_days=
            state.committed_days
            +
            (day_plan,),


        day_stops=(),

        walking_minutes_today=0,

        travel_minutes_today=0,

        attraction_minutes_today=0,


        # Reset only today
        category_counts_today={},


        # KEEP entire trip history
        category_counts_total=
            state.category_counts_total,


        meals_taken_today=
            frozenset(),


        energy=
            min(
                1.0,
                state.energy + 0.4
            ),

    )



# ==========================================================
# Helpers
# ==========================================================


def _add_minutes(
    current_time,
    minutes,
):

    dummy = datetime.combine(
        datetime.today(),
        current_time,
    )


    result = dummy + timedelta(
        minutes=minutes
    )


    return result.time()



def _energy_cost(
    travel,
    visit,
):

    return (
        travel / 600
        +
        visit / 1000
    )
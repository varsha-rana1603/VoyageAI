"""
app/trip_planner/itinerary/planner.py

Beam search itinerary generator.
"""

from __future__ import annotations

from dataclasses import replace
from uuid import UUID

from .models import (
    PlannerState,
    SearchConfig,
    Itinerary,
    Location,
    DayPlan,
)

from .actions import generate_candidates
from .planner_state import apply_move

from .constraints import (
    ConstraintProfile,
    is_legal,
)

from .features import extract_features
from .evaluator import evaluate

from .graph_builder import AttractionGraph
from .route import estimate_route

from ..attractions.models import RankedAttraction


# ==========================================================
# Public API
# ==========================================================


def build_itinerary(
    initial_state: PlannerState,
    ranked_lookup: dict[int, RankedAttraction],
    graph: AttractionGraph,
    profile: ConstraintProfile,
    num_days: int,
    destination_id: UUID,
    config: SearchConfig = SearchConfig(),
) -> Itinerary:


    beam = [
        initial_state
    ]


    finished = []


    step = 0


    while True:

        step += 1

        next_states = []


        for state in beam:


            if state.is_terminal(num_days):

                finished.append(state)
                continue


            moves = generate_candidates(
                state,
                graph,
                ranked_lookup,
                profile,
                config,
            )


            for move in moves:


                new_state = apply_move(
                    state,
                    move,
                    ranked_lookup,
                )


                if not is_legal(
                    move,
                    state,
                    new_state,
                    profile,
                ):
                    continue



                attraction = None
                route = None


                if move.attraction_id is not None:


                    attraction = ranked_lookup[
                        move.attraction_id
                    ]


                    destination = Location(

                        latitude=
                            attraction.latitude,

                        longitude=
                            attraction.longitude,

                        attraction_id=
                            attraction.attraction_id,

                        label=
                            attraction.name,

                    )


                    route = estimate_route(

                        state.current_location,

                        destination,

                    )



                features = extract_features(

                    parent_state=
                        state,

                    resulting_state=
                        new_state,

                    move=
                        move,

                    attraction=
                        attraction,

                    route=
                        route,

                    profile=
                        profile,

                )


                score = evaluate(
                    features
                )


                scored_state = replace(

                    new_state,

                    cumulative_score=
                        (
                            state.cumulative_score
                            +
                            score
                        )

                )


                next_states.append(
                    scored_state
                )



        if not next_states:

            break



        next_states.sort(

            key=lambda s:
                s.cumulative_score,

            reverse=True,

        )


        beam = next_states[
            :config.beam_width
        ]



        if step > 500:

            break



    finished.extend(
        beam
    )


    best = max(

        finished,

        key=lambda s:
            s.cumulative_score,

    )


    return _state_to_itinerary(
        best,
        destination_id,
    )



# ==========================================================
# Conversion
# ==========================================================


def _state_to_itinerary(
    state: PlannerState,
    destination_id: UUID,
) -> Itinerary:


    days = [
        day
        for day in state.committed_days
        if len(day.stops) > 0
    ]


    if state.day_stops:

        days.append(

            DayPlan(

                day_number=
                    state.current_day,

                stops=
                    state.day_stops,

                walking_minutes=
                    state.walking_minutes_today,

                travel_minutes=
                    state.travel_minutes_today,

            )

        )


    return Itinerary(

        destination_id=
            destination_id,

        days=
            tuple(days),

        total_score=
            state.cumulative_score,

        dropped_must_see=(),

    )
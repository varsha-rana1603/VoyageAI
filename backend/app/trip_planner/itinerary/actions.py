"""
app/trip_planner/itinerary/actions.py

Single responsibility: given a state, propose every Move worth
evaluating. Does NOT decide which are legal (constraints.py) or which
are good (features.py + evaluator.py) — this file's only job is "don't
miss a candidate worth considering."

Candidate attraction pool is the UNION of three sources, not any one
alone:
  1. Geographic k-nearest-neighbors of current_location (via the graph,
     or a linear-scan fallback when current_location is a non-attraction
     waypoint — e.g. the hotel at the start of day 2+, which has no
     precomputed graph adjacency).
  2. Top-M globally-ranked unvisited attractions, regardless of distance
     — so a genuinely great attraction across town isn't excluded just
     because it's not geographically close. The evaluator's route/travel
     features are what weigh that trade-off, not a hard distance cutoff.
  3. Any must-see attraction not yet visited — force-included as a
     candidate every step, since constraints.py deliberately does NOT
     enforce must-sees as a hard per-move rule (see its docstring). This
     is where that enforcement actually happens: by making sure a
     must-see is ALWAYS on the table, the evaluator's must-see bonus
     (once features.py adds one) and search itself can prioritize
     working it in before the trip ends.

MoveType.END_TRIP is deliberately never generated here — trip
termination is handled by planner.py checking PlannerState.is_terminal()
after a day ends, not by putting an explicit "end trip" move on the
beam. Keeps this file from needing to know num_days at all.
"""

from __future__ import annotations

from .constraints import ConstraintProfile
from .graph_builder import AttractionGraph
from .models import Move, MoveType, PlannerState, SearchConfig
from ..attractions.models import RankedAttraction


def generate_candidates(
    state: PlannerState,
    graph: AttractionGraph,
    ranked_lookup: dict[int, RankedAttraction],
    profile: ConstraintProfile,
    config: SearchConfig,
) -> list[Move]:
    nearby_ids = _nearby_unvisited_ids(state, graph, ranked_lookup, config.k_nearest)
    top_global_ids = _top_global_unvisited_ids(state, ranked_lookup, config.top_m_global_candidates)
    forced_must_see_ids = profile.must_see_attraction_ids - state.visited_attraction_ids

    attraction_ids = (nearby_ids | top_global_ids | forced_must_see_ids) - profile.excluded_attraction_ids

    candidates: list[Move] = [
        Move(MoveType.VISIT_ATTRACTION, attraction_id=aid) for aid in attraction_ids
    ]

    if "lunch" not in state.meals_taken_today:
        candidates.append(Move(MoveType.TAKE_LUNCH))
    if "dinner" not in state.meals_taken_today:
        candidates.append(Move(MoveType.TAKE_DINNER))

    # Always legal, always proposed -- this is what lets the search choose
    # "stop here" over "squeeze in one more mediocre stop" on its own.
    candidates.append(Move(MoveType.END_DAY))

    return candidates


def _nearby_unvisited_ids(
    state: PlannerState,
    graph: AttractionGraph,
    ranked_lookup: dict[int, RankedAttraction],
    k: int,
) -> set[int]:
    loc = state.current_location

    if loc.attraction_id is not None and loc.attraction_id in graph.adjacency:
        ids = graph.neighbors_of(loc.attraction_id, k=k)
    else:
        # Non-attraction waypoint (e.g. hotel at the start of a day) has no
        # precomputed adjacency. Linear scan is fine at this scale (~100
        # attractions/destination) -- not worth precomputing a spatial
        # index for a handful of these lookups per search run.
        scored = sorted(
            (
                (aid, graph.distance_from_point_km(loc.latitude, loc.longitude, aid))
                for aid in ranked_lookup
                if aid in graph.locations
            ),
            key=lambda pair: pair[1],
        )
        ids = [aid for aid, _ in scored[:k]]

    return {aid for aid in ids if aid not in state.visited_attraction_ids}


def _top_global_unvisited_ids(
    state: PlannerState,
    ranked_lookup: dict[int, RankedAttraction],
    m: int,
) -> set[int]:
    unvisited = sorted(
        (
            (aid, ranked.score)
            for aid, ranked in ranked_lookup.items()
            if aid not in state.visited_attraction_ids
        ),
        key=lambda pair: pair[1],
        reverse=True,
    )
    return {aid for aid, _ in unvisited[:m]}
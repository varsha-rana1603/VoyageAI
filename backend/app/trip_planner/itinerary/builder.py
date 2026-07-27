"""
app/trip_planner/itinerary/builder.py

Entry point for itinerary generation.

Responsibilities:
    - Build attraction graph
    - Create initial planner state
    - Start beam search

Does NOT:
    - allocate days
    - schedule attractions
    - optimize routes

The search algorithm owns itinerary construction.
"""

from __future__ import annotations

from uuid import UUID

from .models import (
    PlannerState,
    Location,
    SearchConfig,
    Itinerary,
)

from .planner import build_itinerary
from .graph_builder import build_graph
from .constraints import ConstraintProfile

from ..attractions.models import RankedAttraction



def generate_itinerary(
    destination_id: UUID,
    destination_latitude: float,
    destination_longitude: float,
    ranked_attractions: list[RankedAttraction],
    profile: ConstraintProfile,
    num_days: int,
    config: SearchConfig = SearchConfig(),
) -> Itinerary:


    # --------------------------------------------------
    # Create lookup table
    # --------------------------------------------------

    ranked_lookup = {
        attraction.attraction_id: attraction
        for attraction in ranked_attractions
    }


    # --------------------------------------------------
    # Build attraction graph
    # --------------------------------------------------

    graph = build_graph(
        ranked_attractions,
        k=config.k_nearest,
    )


    # --------------------------------------------------
    # Initial state
    # --------------------------------------------------

    initial_location = Location(

        latitude=
            destination_latitude,

        longitude=
            destination_longitude,

        attraction_id=None,

        label="Hotel",

    )


    initial_state = PlannerState(

        current_day=1,

        current_time=
            profile.daily_start,

        current_location=
            initial_location,

    )


    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    return build_itinerary(

        initial_state=

            initial_state,

        ranked_lookup=

            ranked_lookup,

        graph=

            graph,

        profile=

            profile,

        num_days=

            num_days,

        destination_id=

            destination_id,

        config=

            config,

    )
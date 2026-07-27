"""
app/trip_planner/itinerary/route.py

Single responsibility: estimate travel time, distance, and mode between
two Locations. Works for any pair — attraction-to-attraction (uses the
graph's precomputed distance where available), or waypoint-to-attraction
(hotel/start point isn't in the graph's adjacency, so this always falls
back to a direct Haversine calc via graph.distance_from_point_km / a
plain haversine_km call).

Self-contained, same reasoning as graph_builder.py: not importing
trip_planner/planner/transportation.py, since that package's fate is
still undecided. If/when that's settled, swap this file's internals for
a delegate call — the public `estimate_route()` signature doesn't need
to change either way, so nothing downstream (actions.py, features.py)
would need to know the difference.

Mode-selection bands and speeds are the same heuristic values used in
the old planner/transportation.py — duplicated deliberately rather than
imported, not because the numbers themselves changed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .graph_builder import haversine_km
from .models import Location

_WALK_KMH = 4.5
_METRO_KMH = 28.0
_TAXI_KMH = 22.0

_WALK_MAX_KM = 1.2
_TRANSIT_PREFERRED_MAX_KM = 8.0

_ROUTING_INFLATION = 1.35  # straight-line -> approximate real street/track routing
_TRANSIT_BOARDING_OVERHEAD_MINUTES = 8.0  # fixed wait/board overhead for non-walking modes


class TransportMode(str, Enum):
    WALK = "walk"
    METRO = "metro"
    TAXI = "taxi"


@dataclass(frozen=True)
class RouteEstimate:
    mode: TransportMode
    duration_minutes: float
    distance_km: float


def estimate_route(origin: Location, destination: Location) -> RouteEstimate:
    straight_km = haversine_km(
        origin.latitude, origin.longitude, destination.latitude, destination.longitude
    )
    distance_km = straight_km * _ROUTING_INFLATION

    if distance_km <= _WALK_MAX_KM:
        mode = TransportMode.WALK
        speed_kmh = _WALK_KMH
    elif distance_km <= _TRANSIT_PREFERRED_MAX_KM:
        mode = TransportMode.METRO
        speed_kmh = _METRO_KMH
    else:
        mode = TransportMode.TAXI
        speed_kmh = _TAXI_KMH

    duration_minutes = (distance_km / speed_kmh) * 60
    if mode != TransportMode.WALK:
        duration_minutes += _TRANSIT_BOARDING_OVERHEAD_MINUTES

    return RouteEstimate(
        mode=mode,
        duration_minutes=round(duration_minutes, 1),
        distance_km=round(distance_km, 3),
    )
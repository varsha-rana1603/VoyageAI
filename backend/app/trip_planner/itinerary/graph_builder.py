"""
app/trip_planner/itinerary/graph_builder.py

Single responsibility: turn a list of attractions into an
AttractionGraph — each attraction's precomputed k-nearest-neighbors by
Haversine distance.

Deliberately independent of planner.py, actions.py, and evaluator.py —
this file only knows about geography, nothing about search or scoring,
per the requirement that the graph builder be independent from the
planner. Swapping Haversine for a real routing API later means editing
ONLY this file's distance calculation; nothing downstream changes,
since callers consume AttractionGraph.neighbors_of()/.distance_km(),
never raw coordinates directly.

Not importing trip_planner/planner/transportation.py's haversine_km —
that package's fate is still undecided, and duplicating one ~10-line
function here is cheaper than a cross-package import that might not
resolve if that file never actually gets deployed. If/when that's
settled, this can delegate there instead.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.trip_planner.attractions.models import AttractionLike


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


@dataclass(frozen=True)
class AttractionGraph:
    # attraction_id -> [(neighbor_id, distance_km), ...], nearest-first, capped at k
    adjacency: dict[int, list[tuple[int, float]]]
    # attraction_id -> (lat, lng), for ad-hoc distance lookups outside the precomputed k
    locations: dict[int, tuple[float, float]]

    def neighbors_of(self, attraction_id: int, k: int | None = None) -> list[int]:
        entries = self.adjacency.get(attraction_id, [])
        if k is not None:
            entries = entries[:k]
        return [aid for aid, _ in entries]

    def distance_km(self, attraction_id_a: int, attraction_id_b: int) -> float:
        """Prefers the precomputed adjacency; falls back to a fresh
        Haversine calc for pairs outside the k-nearest set — e.g. a
        top-M globally-ranked candidate that isn't geographically close
        to current_location. Both attraction ids must exist in
        `locations` (i.e. were passed to build_graph()).
        """
        for neighbor_id, dist in self.adjacency.get(attraction_id_a, []):
            if neighbor_id == attraction_id_b:
                return dist
        lat_a, lng_a = self.locations[attraction_id_a]
        lat_b, lng_b = self.locations[attraction_id_b]
        return haversine_km(lat_a, lng_a, lat_b, lng_b)

    def distance_from_point_km(self, latitude: float, longitude: float, attraction_id: int) -> float:
        """For distance from an arbitrary point (hotel/start Location)
        to an attraction — not every 'current_location' is itself an
        attraction with graph adjacency.
        """
        lat_b, lng_b = self.locations[attraction_id]
        return haversine_km(latitude, longitude, lat_b, lng_b)


def build_graph(attractions: list[AttractionLike], k: int = 10) -> AttractionGraph:
    print("ATTRACTION", attractions[0])
    locations = {a.attraction_id: (a.latitude, a.longitude) for a in attractions}

    adjacency: dict[int, list[tuple[int, float]]] = {}
    for a in attractions:
        distances = [
            (b.attraction_id, haversine_km(a.latitude, a.longitude, b.latitude, b.longitude))
            for b in attractions
            if b.attraction_id != a.attraction_id
        ]
        distances.sort(key=lambda pair: pair[1])
        adjacency[a.attraction_id] = distances[:k]

    return AttractionGraph(adjacency=adjacency, locations=locations)
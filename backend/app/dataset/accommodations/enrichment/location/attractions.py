from app.trip_planner.domain.accommodation import Accommodation
from app.trip_planner.domain.attraction import Attraction

from .city_center import haversine_distance_km


def compute_attraction_distance(
    accommodation: Accommodation,
    attractions: list[Attraction],
) -> Accommodation:
    """
    Computes the average distance to the five nearest attractions.
    """

    if not attractions:
        accommodation.distance_to_main_attractions_km = None
        return accommodation

    distances = []

    for attraction in attractions:
        distance = haversine_distance_km(
            accommodation.coordinates.latitude,
            accommodation.coordinates.longitude,
            attraction.coordinates.latitude,
            attraction.coordinates.longitude,
        )

        distances.append(distance)

    distances.sort()

    nearest = distances[:5]

    accommodation.distance_to_main_attractions_km = round(
        sum(nearest) / len(nearest),
        2,
    )

    return accommodation
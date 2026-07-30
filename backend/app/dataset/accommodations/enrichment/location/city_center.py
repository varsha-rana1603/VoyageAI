from app.trip_planner.domain.accommodation import Accommodation
from app.trip_planner.domain.destination import DestinationInfo
from app.utils.geo import haversine_distance_km

def compute_city_center_distance(
    accommodation: Accommodation,
    destination,
) -> Accommodation:

    accommodation.distance_to_city_center_km = (
        haversine_distance_km(
            accommodation.coordinates.latitude,
            accommodation.coordinates.longitude,
            destination.latitude,
            destination.longitude,
        )
    )

    return accommodation
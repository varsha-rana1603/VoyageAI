from app.trip_planner.domain.accommodation import Accommodation


CITY_AVERAGE_SPEED_KMPH = 25.0


def estimate_average_travel_time(
    accommodation: Accommodation,
) -> Accommodation:
    """
    Estimates average driving time to nearby attractions.
    """

    if accommodation.distance_to_main_attractions_km is None:
        accommodation.average_travel_time_minutes = None
        return accommodation

    minutes = (
        accommodation.distance_to_main_attractions_km
        / CITY_AVERAGE_SPEED_KMPH
    ) * 60

    accommodation.average_travel_time_minutes = round(
        minutes,
        1,
    )

    return accommodation
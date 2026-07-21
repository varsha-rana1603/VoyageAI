from typing import Literal
from pydantic import BaseModel

class NearbyDestination(BaseModel):
    #A destination that can reasonably be combined with the main destination
    name: str
    country: str
    distance_km: float
    travel_time_minutes: int
    transport_modes: list[str]
    visit_type: Literal[
        "day_trip",
        "overnight",
        "multi_day"
    ]
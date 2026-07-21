from pydantic import BaseModel
from .common import Coordinates

class DestinationInfo(BaseModel):
    #Immutable info describing the selected destination
    name: str
    country: str
    coordinates: Coordinates
    timezone: str
    currency: str
    google_place_id: str

class DestinationMetadata(BaseModel):
    #Metadeta produced by VoyageAI's ingestion pipeline
    description: str
    terrain: list[str]
    travel_styles: list[str]
    best_season: str
    worst_season: str
    crowd_level: str
    cost_profile: dict

    
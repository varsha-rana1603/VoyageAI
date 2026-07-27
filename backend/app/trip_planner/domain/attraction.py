from typing import Literal 
from pydantic import BaseModel # type: ignore
from .common import Coordinates, Money

class Attraction(BaseModel):
    #Represents one attraction within a destination
    name: str
    category: str
    description: str | None = None
    coordinates: Coordinates
    google_place_id: str
    rating: float | None = None
    review_count: int | None = None
    popularity_score: float | None = None
    website: str | None = None
    importance: Literal[
        "must_visit",
        "highly_recommended",
        "interest_based",
        "optional"
    ] | None = None
    visit_duration_minutes: int | None = None
    estimated_ticket_price: Money | None = None
    opening_hours: list[str] = []
    indoor: bool | None = None
    family_friendly: bool | None = None
    tags: list[str] = []
    is_free: bool | None = None
    
    
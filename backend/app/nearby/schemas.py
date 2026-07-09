#Data contract for the Destination Exploration Feature
#All moduls in app/nearby/ is built against these shapes

from typing import Optional
from pydantic import BaseModel

#Request
class ExploreRequest(BaseModel):
    destination_name: str
    travel_style: str
    budget: str
    crowd_tolerance: str
    terrain: str
    free_text: str = ""


#Internal shaped
class RawSight(BaseModel):
    #Normalised Google Places Result
    #sight_cache.py will store this per destination - same data reused across every user who explores that destination
    place_id: str
    name: str
    lat: float
    lon: float
    rating: Optional[float] = None
    review_count: Optional[float] = None
    category: str #"culture" | "nature" | "food" | "shopping"
    raw_types: list[str] = []


class CategoryWeights(BaseModel):
    #Output of preference_engine.py - how much this specific user cares about each category
    #Derived from user_profile + free_text

    culture: float
    nature: float
    food: float
    shoopping: float

#Response

class NearbySightRef(BaseModel):
    name: str
    distance_km:float

class NearbyStayRef(BaseModel): 
    name: str
    distance_km: float

class RecommendationStayOut(BaseModel):
    name: str
    score: int
    why: str
    nearby_sights: list[NearbySightRef]

class SightOut(BaseModel):
    name: str
    rating: Optional[float]
    review_count: Optional[int]
    category: str
    score: int
    why: str
    recommended_stay: list[NearbyStayRef]

class ExploreResponse(BaseModel):
    destination: str
    recommended_stays: list[RecommendationStayOut]
    sights: list[SightOut]


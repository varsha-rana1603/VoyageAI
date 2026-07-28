from typing import Literal
from pydantic import BaseModel, Field


class HotelSemanticFeatures(BaseModel):
    brand_name: str | None = None
    brand_tier: str | None = None
    hotel_category: str
    estimated_stars: int
    luxury_positioning: float
    location_type: str
    location_quality_score: float
    pool: bool = False
    spa: bool = False
    business_friendly: bool = False
    family_friendly: bool = False   
    best_for: list[str] = Field(
        default_factory=list
    )
    confidence: float

class HotelEnrichmentResponse(BaseModel):
    """
    Response returned from the LLM for a batch of hotels.
    """
    hotels: list[HotelSemanticFeatures]
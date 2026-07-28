from typing import Any, Literal

from pydantic import BaseModel, Field

from .common import Coordinates


class Accommodation(BaseModel):

    # ---------------------------------------------------------
    # Identity
    # ---------------------------------------------------------

    name: str
    google_place_id: str
    coordinates: Coordinates


    # ---------------------------------------------------------
    # Basic information
    # ---------------------------------------------------------

    lodging_type: str | None = None
    description: str | None = None
    website: str | None = None


    # ---------------------------------------------------------
    # Google signals
    # ---------------------------------------------------------

    rating: float | None = None
    review_count: int | None = None


    # ---------------------------------------------------------
    # Pricing
    # ---------------------------------------------------------

    estimated_price_per_night: float | None = None

    currency: str = "AED"

    pricing_source: str | None = None

    pricing_confidence: float | None = None

    price_tier: Literal[
        "budget",
        "mid_range",
        "luxury",
    ] | None = None


    # ---------------------------------------------------------
    # Amenities
    # ---------------------------------------------------------

    amenities: list[str] = Field(default_factory=list)

    pool: bool | None = None
    spa: bool | None = None

    family_friendly: bool | None = None
    business_friendly: bool | None = None


    # ---------------------------------------------------------
    # Planner metadata
    # ---------------------------------------------------------

    tags: list[str] = Field(default_factory=list)

    star_rating: int | None = None

    best_for: list[str] = Field(default_factory=list)

    distance_to_city_center_km: float | None = None

    distance_to_nearest_metro_km: float | None = None

    planner_metadata: dict[str, Any] = Field(
        default_factory=dict
    )


    # ---------------------------------------------------------
    # AI Embeddings
    # ---------------------------------------------------------

    embedding_text: str | None = None

    embedding: list[float] | None = None


    # ---------------------------------------------------------
    # AI Enrichment
    # ---------------------------------------------------------

    brand_name: str | None = None

    brand_tier: Literal[
        "budget",
        "midscale",
        "upscale",
        "luxury",
        "ultra_luxury",
    ] | None = None


    hotel_category: str | None = None

    luxury_positioning: float | None = None

    location_type: str | None = None

    location_quality_score: float | None = None

    quality_score: float | None = None


    semantic_features: dict[str, Any] = Field(
        default_factory=dict
    )

    enrichment_confidence: float | None = None

    enrichment_source: str | None = None
    score: float | None = None

    reasons: list[str] = Field(
        default_factory=list
    )
    luxury_score: float | None = None

    business_score: float | None = None

    family_score: float | None = None

    romantic_score: float | None = None

    wellness_score: float | None = None

    budget_score: float | None = None
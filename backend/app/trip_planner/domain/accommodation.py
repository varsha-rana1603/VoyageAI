from typing import Any, Literal

from pydantic import BaseModel, Field

from .common import Coordinates


class Accommodation(BaseModel):
    """Represents one accommodation option within a destination."""

    # -----------------------------
    # Identity
    # -----------------------------
    name: str
    google_place_id: str
    coordinates: Coordinates

    # -----------------------------
    # Basic Information
    # -----------------------------
    lodging_type: str | None = None
    description: str | None = None
    website: str | None = None

    # -----------------------------
    # Google Signals
    # -----------------------------
    rating: float | None = None
    review_count: int | None = None

    # -----------------------------
    # Planning Metadata
    # -----------------------------
    price_tier: Literal["budget", "mid_range", "luxury"] | None = None

    amenities: list[str] = Field(default_factory=list)

    pool: bool | None = None
    spa: bool | None = None

    # Keep these for now.
    # Later we can replace them with scores if needed.
    family_friendly: bool | None = None
    business_friendly: bool | None = None

    tags: list[str] = Field(default_factory=list)

    planner_metadata: dict[str, Any] = Field(default_factory=dict)

    # -----------------------------
    # AI Metadata
    # -----------------------------
    embedding_text: str | None = None

    # photo_references: list[str] = Field(default_factory=list)

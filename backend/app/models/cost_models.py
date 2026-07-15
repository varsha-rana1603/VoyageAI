"""
Pydantic schemas shared by the cost pipeline.

These are the contract between cost_provider.get_city_cost_data() and
downstream consumers (cost_loader.py, the PostgreSQL JSONB ingestion job).
Keeping them as explicit models -- rather than raw dicts -- means schema
drift gets caught at ingestion time instead of silently corrupting rows
in Postgres.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CostTier(str, Enum):
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    LUXURY = "luxury"


class CategoryCosts(BaseModel):
    """Daily spend per category, in the destination's local currency."""

    accommodation: float = Field(..., ge=0)
    food: float = Field(..., ge=0)
    transport: float = Field(..., ge=0)
    activities: float = Field(..., ge=0)
    misc: float = Field(..., ge=0)


class DailyCost(BaseModel):
    budget: CategoryCosts
    mid_range: CategoryCosts
    luxury: CategoryCosts


class CostConfidence(str, Enum):
    """
    How the numbers were produced. cost_loader / the ingestion job can use
    this to decide whether to flag a row for manual review, weight it
    differently in scoring, or trigger a re-fetch later once a better
    source becomes available.
    """

    MODELED = "modeled"          # baseline + tier model only
    WIKIVOYAGE_ENRICHED = "wikivoyage_enriched"  # model, adjusted by mined text
    LOW_CONFIDENCE = "low_confidence"            # one or more signals missing/defaulted


class CityCostProfile(BaseModel):
    city: str
    country: str
    currency: str
    daily_cost: DailyCost
    source: str
    confidence: CostConfidence = CostConfidence.MODELED

    def to_storage_dict(self) -> dict:
        """Shape stored as JSONB in Postgres -- matches the schema the user specified."""
        return {
            "currency": self.currency,
            "daily_cost": {
                "budget": self.daily_cost.budget.model_dump(),
                "mid_range": self.daily_cost.mid_range.model_dump(),
                "luxury": self.daily_cost.luxury.model_dump(),
            },
            "source": self.source,
            "confidence": self.confidence.value,
        }

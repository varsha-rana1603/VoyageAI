"""
app/trip_planner/attractions/models.py

Contracts for this package only. Two Protocols describe the fields the
ranker needs from your real `app/models/` Attraction and UserProfile
classes — these are NOT new domain models, just a structural checklist.
Your real classes satisfy them automatically as long as field names
match; no adapter/wrapper object needed.

Verified against the real `app/models/attraction.py` (2026-07-26):
  - `id` is `Integer` (autoincrement PK), NOT a UUID — only `destination_id`
    is UUID (FK to `destinations.id`).
  - Tier field is called `importance`, not `prominence_tier`.
  - Duration field is `visit_duration_minutes`, not `avg_visit_duration_minutes`.
  - `tags` is a JSONB column — assumed to deserialize to `list[str]` per
    the ingestion enrichment step; flag if it's actually stored as a dict.

Verified against the real `app/models/user_profile.py` (2026-07-26):
  - No `has_kids` bool — instead `is_family: bool` and `children: Optional[int]`.
  - No `budget_tier` string — instead raw `total_budget`/`minimum_budget`/
    `maximum_budget` (assumed AED, per the destination budget profile
    convention). No tier label exists on the profile itself.
  - Six granular 1-5 `*_importance` scores (food/nightlife/adventure/
    relaxation/culture/nature) — a stronger signal than flat tag matching,
    now used by a dedicated `lifestyle_importance_fit` factor.
  - `must_visit: List[str]` exists but is NOT handled by this package —
    see note in ranker.py. It's free-text names collected before a
    destination was chosen, so it needs name resolution against real
    attraction rows before it can drive a hard include/boost. Don't
    assume it's silently covered by scoring.

RankedAttraction / RankingFactor are genuinely new — nothing upstream
produces them, so they're owned here.
"""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable
from uuid import UUID

from pydantic import BaseModel, Field


@runtime_checkable
class AttractionLike(Protocol):
    id: int
    destination_id: UUID
    name: str
    category: str
    latitude: float
    longitude: float
    popularity_score: float | None
    importance: str | None
    rating: float | None
    review_count: int | None
    visit_duration_minutes: int | None
    is_free: bool | None
    indoor: bool | None
    family_friendly: bool | None
    tags: list[str]
    # -------------------------
    # Intelligence features
    # -------------------------
    historical_score: float | None
    architecture_score: float | None
    photography_score: float | None
    crowd_score: float | None
    hidden_gem_score: float | None
    estimated_cost: float | None = None
    best_visit_times: list[str] = []
    experience_tags: list[str] = []


@runtime_checkable
class UserProfileLike(Protocol):
    travel_styles: list[str]
    exploration_interests: list[str]
    terrain_preferences: list[str]
    crowd_preference: Optional[str]  # "avoid_crowds" | "neutral" | "seek_popular"

    is_family: bool
    children: Optional[int]

    total_budget: Optional[int]
    minimum_budget: Optional[int]
    maximum_budget: Optional[int]
    duration_days: Optional[int]
    traveller_count: Optional[int]
    adults: Optional[int]

    food_importance: Optional[int]
    nightlife_importance: Optional[int]
    adventure_importance: Optional[int]
    relaxation_importance: Optional[int]
    culture_importance: Optional[int]
    nature_importance: Optional[int]


class RankingFactor(BaseModel):
    name: str
    weight: float
    raw_score: float = Field(ge=0.0, le=1.0)
    contribution: float


class RankedAttraction(BaseModel):
    attraction_id: int
    name: str
    category: str
    score: float
    factors: list[RankingFactor]
    explanation: str
    latitude: float
    longitude: float
    visit_duration_minutes: int
    tags: list[str]
    rating: float | None
    popularity_score: float
    family_friendly: bool | None
    is_free: bool | None
    iconic_score: float = 0
    destination_fit_score: float = 0
    tourist_priority_score: float = 0
    category_quality_score: float = 0
    historical_score: float = 0
    architecture_score: float = 0
    photography_score: float = 0
    crowd_score: float = 0
    hidden_gem_score: float = 0
    opening_hours: dict | list[str] | None = None
    estimated_cost: float = 0
    best_visit_times: list[str] = []
    experience_tags: list[str] = []
import uuid

from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    profile_id: uuid.UUID
    limit: int = 5


class DestinationRecommendation(BaseModel):
    destination_id: uuid.UUID
    name: str
    country: str
    match_score: float
    estimated_cost_inr: float
    within_budget: bool
    reason: str  # short, deterministic explanation -- see ranking_service.explain()


class RecommendationResponse(BaseModel):
    profile_id: uuid.UUID
    recommendations: list[DestinationRecommendation]

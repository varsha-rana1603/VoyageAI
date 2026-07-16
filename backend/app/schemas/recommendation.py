from uuid import UUID

from pydantic import BaseModel

from app.conversation.user_profile import UserProfile


class RecommendationRequest(BaseModel):
    profile: UserProfile
    top_k: int = 10


class Recommendation(BaseModel):
    destination_id: UUID
    name: str
    country: str

    score: float

    reason: str | None = None


class RecommendationResponse(BaseModel):
    recommendations: list[Recommendation]
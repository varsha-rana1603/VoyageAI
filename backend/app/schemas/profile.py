import uuid

from pydantic import BaseModel


class ConversationMessageIn(BaseModel):
    profile_id: uuid.UUID | None = None  # None on the very first turn
    user_id: uuid.UUID
    message: str


class ConversationMessageOut(BaseModel):
    profile_id: uuid.UUID
    ai_reply: str
    extracted_fields: dict  # only the fields newly filled this turn
    is_complete: bool  # True once enough fields exist to run ranking


class TravellerProfileOut(BaseModel):
    id: uuid.UUID
    travel_style: str | None
    budget_tier: str | None
    crowd_tolerance: str | None
    trip_duration_days: int | None

    model_config = {"from_attributes": True}

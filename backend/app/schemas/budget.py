import uuid

from pydantic import BaseModel


class BudgetBreakdown(BaseModel):
    destination_id: uuid.UUID
    profile_id: uuid.UUID
    trip_duration_days: int
    estimated_cost_inr: float
    base_cost_inr: float
    cost_per_day_inr: float
    within_budget: bool
    budget_tier: str

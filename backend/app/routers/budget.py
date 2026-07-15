import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.destination import Destination
from app.models.profile import TravellerProfile
from app.schemas.budget import BudgetBreakdown
from app.services.budget_service import budget_breakdown

router = APIRouter(prefix="/api/destinations", tags=["budget"])


@router.get("/{destination_id}/budget", response_model=BudgetBreakdown)
def get_budget(destination_id: uuid.UUID, profile_id: uuid.UUID, db: Session = Depends(get_db)):
    destination = db.get(Destination, destination_id)
    profile = db.get(TravellerProfile, profile_id)
    if destination is None or profile is None:
        raise HTTPException(status_code=404, detail="Destination or profile not found")

    duration = profile.trip_duration_days or 5
    return budget_breakdown(destination, duration, user_budget_inr=None, budget_tier=profile.budget_tier)
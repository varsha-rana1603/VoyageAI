from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.traveller_profile import TravellerProfile
from backend.app.schemas.chat import ConversationMessageIn, ConversationMessageOut, TravellerProfileOut
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.post("/message", response_model=ConversationMessageOut)
def send_message(payload: ConversationMessageIn, db: Session = Depends(get_db)):
    service = ProfileService(db)
    profile, extracted = service.process_message(payload.user_id, payload.profile_id, payload.message)
    return ConversationMessageOut(
        profile_id=profile.id,
        ai_reply=service.next_question(profile),
        extracted_fields=extracted,
        is_complete=ProfileService.is_complete(profile),
    )


@router.get("/{profile_id}", response_model=TravellerProfileOut)
def get_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.get(TravellerProfile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

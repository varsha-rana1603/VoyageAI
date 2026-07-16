#Main pipeline

from sqlalchemy.orm import Session
from app.conversation.user_profile import UserProfile

def recommend_destinations(db: Session, profile: UserProfile, top_k: int = 10):
    raise NotImplementedError


#embeds user profile and queries PostgreSQL vector
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.conversation.user_profile import UserProfile
from app.ml.embeddings import embed_profile
from app.models.destination import Destination

@dataclass
class CandidateDestination:
    destination: Destination
    semantic_score: float

def retreive_candidates(
        db: Session,
        profile: UserProfile,
        top_k: int = 100
) -> list[Destination]:
    #Retrieves the most sementically similar destinations using pgvector cosine similarity
    user_embedding = embed_profile(profile)

    results = (
        db.query(
            Destination,
            Destination.embedding.cosine_distance(
                user_embedding
            ).label("distance")
        ).order_by("distance").limit(top_k).all()
    )
    
def final_candidate_destinations(db: Session, embedding: list[float], limit: int = 100):
    #Retrieve the most sementically similar destinations using pgvector
    raise NotImplementedError


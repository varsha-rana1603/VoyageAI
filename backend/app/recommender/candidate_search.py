#embeds user profile and queries PostgreSQL vector
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.conversation.user_profile import UserProfile
from app.ml.embeddings import profile_to_embedding_text, embed_text
from app.models.destination import Destination

@dataclass
class CandidateDestination:
    destination: Destination
    semantic_score: float
    final_score: float = 0.0
    reasons: list[str] | None = None

def retrieve_candidates(
        db: Session,
        profile: UserProfile,
        top_k: int = 100
) -> list[CandidateDestination]:
    #Retrieves the most sementically similar destinations using pgvector cosine similarity
    text = profile_to_embedding_text(profile)
    user_embedding = embed_text(text)

    results = (
        db.query(
            Destination,
            Destination.destination_embedding.cosine_distance(
                user_embedding
            ).label("distance")
        ).order_by("distance").limit(top_k).all()
    )
    candidates: list[CandidateDestination] = []

    for destination, distance in results:
        #Convert cosine distance into a similarity score
        #Smaller distance = higher similarity ( 0 distance = 1 similarity)
        semantic_score = 1.0 - float(distance)

        candidates.append(
            CandidateDestination(
                destination=destination,
                semantic_score=semantic_score
            )
        )
    return candidates
    


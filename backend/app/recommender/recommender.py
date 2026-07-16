from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.conversation.user_profile import UserProfile
from app.models.destination import Destination
from app.recommender.candidate_search import (
    CandidateDestination,
    retrieve_candidates,
)
from app.recommender.reasons import generate_reasons
from app.recommender.scoring import (
    build_matched_features,
    calculate_final_score,
)


@dataclass
class RankedDestination:
    destination: Destination
    score: float
    candidate: CandidateDestination
    reasons: list[str]


def recommend_destinations(
    db: Session,
    profile: UserProfile,
    top_k: int = 10,
) -> list[RankedDestination]:
    """
    Complete recommendation pipeline.

    1. Embed user profile
    2. Retrieve top semantic candidates
    3. Score candidates
    4. Select top K
    5. Generate explanation reasons using a single LLM call
    """

    # Retrieve semantic candidates
    candidates = retrieve_candidates(
        db=db,
        profile=profile,
        top_k=100,
    )

    ranked: list[RankedDestination] = []

    # Score every candidate
    for candidate in candidates:

        score = calculate_final_score(
            profile=profile,
            candidate=candidate,
        )

        ranked.append(
            RankedDestination(
                destination=candidate.destination,
                score=score,
                candidate=candidate,
                reasons=[],
            )
        )

    # Highest score first
    ranked.sort(
        key=lambda x: x.score,
        reverse=True,
    )

    # Keep only top K
    ranked = ranked[:top_k]

    # ----------------------------
    # Build payload for Bedrock
    # ----------------------------

    llm_payload = []

    for item in ranked:

        llm_payload.append(
            {
                "destination": item.destination.name,
                "matched_features": build_matched_features(
                    profile=profile,
                    candidate=item.candidate,
                ),
            }
        )

    # ----------------------------
    # Generate polished reasons
    # ----------------------------

    generated_reasons = generate_reasons(
        llm_payload
    )

    # ----------------------------
    # Attach reasons
    # ----------------------------

    for item in ranked:

        item.reasons = generated_reasons.get(
            item.destination.name,
            [],
        )

    return ranked
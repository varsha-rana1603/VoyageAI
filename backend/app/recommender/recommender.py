import logging
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.conversation.user_profile import UserProfile
from app.models.destination import Destination
from app.recommender.candidate_search import (
    CandidateDestination,
    CandidateRetrievalError,
    retrieve_candidates,
)
from app.recommender.reasons import generate_reasons
from app.recommender.scoring import (
    ComponentScores,
    build_matched_features,
    calculate_final_score,
    score_candidate,
)

logger = logging.getLogger(__name__)


@dataclass
class RankedDestination:
    destination: Destination
    score: float
    candidate: CandidateDestination
    reasons: list[str]
    components: ComponentScores | None = field(default=None)


def recommend_destinations(
    db: Session,
    profile: UserProfile,
    top_k: int = 10,
) -> list[RankedDestination]:
    """
    Complete recommendation pipeline.

    1. Embed user profile + retrieve top semantic candidates
    2. Score every candidate (component scores computed once, reused for
       both the final weighted score and the matched-feature explanations)
    3. Select top K
    4. Generate polished explanations using a single LLM call, with a
       deterministic fallback if that call fails
    """

    try:
        candidates = retrieve_candidates(db=db, profile=profile, top_k=100)
    except CandidateRetrievalError:
        # Let the caller (route handler) decide how to surface this —
        # e.g. a 503 with a friendly message — rather than a raw 500.
        raise

    if not candidates:
        return []

    ranked: list[RankedDestination] = []

    for candidate in candidates:
        components = score_candidate(profile=profile, candidate=candidate)
        score = calculate_final_score(components)

        ranked.append(
            RankedDestination(
                destination=candidate.destination,
                score=score,
                candidate=candidate,
                reasons=[],
                components=components,
            )
        )

    ranked.sort(key=lambda x: x.score, reverse=True)
    ranked = ranked[:top_k]

    llm_payload = [
        {
            "destination": item.destination.name,
            "matched_features": build_matched_features(
                profile=profile,
                candidate=item.candidate,
                components=item.components,
            ),
        }
        for item in ranked
    ]

    generated_reasons = generate_reasons(llm_payload)

    for item in ranked:
        item.reasons = generated_reasons.get(item.destination.name, [])

    return ranked
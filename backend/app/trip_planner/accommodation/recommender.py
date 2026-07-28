"""
Accommodation recommendation pipeline.

Pipeline
--------
Fetch Candidates
        ↓
Filter
        ↓
Score
        ↓
Rank
        ↓
Return Top Recommendations
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.trip_planner.domain.accommodation import Accommodation
from app.conversation.user_profile import UserProfile

from .fetcher import fetch_candidate_accommodations
from .filters import filter_accommodations
from .ranking import top_accommodations


# ---------------------------------------------------------
# Recommender
# ---------------------------------------------------------

def recommend_accommodations(
    *,
    db: Session,
    destination_id: UUID,
    user_profile: UserProfile,
    limit: int = 3,
) -> list[Accommodation]:
    """
    Recommend the best accommodations for a destination.

    Parameters
    ----------
    db
        SQLAlchemy session.

    destination_id
        Destination UUID.

    user_profile
        User preferences.

    limit
        Number of accommodations to return.

    Returns
    -------
    list[Accommodation]
    """

    print("\nFetching accommodation candidates...")

    accommodations = fetch_candidate_accommodations(
        db=db,
        destination_id=destination_id,
    )

    print(
        f"Retrieved {len(accommodations)} accommodations."
    )

    print("\nApplying recommendation filters...")

    accommodations = filter_accommodations(
        accommodations,
        user_profile,
    )

    print(
        f"{len(accommodations)} accommodations remain."
    )

    print("\nRanking accommodations...")

    recommendations = top_accommodations(
        accommodations=accommodations,
        user_profile=user_profile,
        k=limit,
    )

    print(
        f"Returning top {len(recommendations)} accommodations."
    )

    return recommendations
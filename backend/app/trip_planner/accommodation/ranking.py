"""
Accommodation ranking.

Responsibilities
----------------
✓ Rank accommodations by recommendation score
✓ Return top-k recommendations

Not responsible for
-------------------
✗ Database queries
✗ Filtering
✗ Score calculation
"""

from app.trip_planner.domain.accommodation import Accommodation
from app.conversation.user_profile import UserProfile

from .scoring import overall_score


# ---------------------------------------------------------
# Rank
# ---------------------------------------------------------

def rank_accommodations(
    accommodations: list[Accommodation],
    user_profile: UserProfile,
) -> list[Accommodation]:
    """
    Rank accommodations from best to worst.
    """

    scored = []

    for accommodation in accommodations:

        score = overall_score(
            accommodation,
            user_profile,
        )

        accommodation.score = score

        scored.append(
            accommodation
        )

    return sorted(
        scored,
        key=lambda accommodation: accommodation.score or 0,
        reverse=True,
    )


# ---------------------------------------------------------
# Top K
# ---------------------------------------------------------

def top_accommodations(
    accommodations: list[Accommodation],
    user_profile: UserProfile,
    k: int = 3,
) -> list[Accommodation]:
    """
    Return the top-k recommended accommodations.
    """

    ranked = rank_accommodations(
        accommodations,
        user_profile,
    )

    return ranked[:k]
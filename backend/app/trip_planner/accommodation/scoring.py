"""
Accommodation recommendation scoring.

Responsibilities
----------------
✓ Compute recommendation scores
✓ Combine multiple signals into one score

Not responsible for
-------------------
✗ Database queries
✗ Filtering
✗ Ranking
"""

from app.trip_planner.domain.accommodation import Accommodation
from app.conversation.user_profile import UserProfile


# ---------------------------------------------------------
# Budget
# ---------------------------------------------------------

def budget_score(
    accommodation: Accommodation,
    user_profile: UserProfile,
) -> float:
    """
    Score how well accommodation price fits user budget.
    """

    budget = (
        user_profile.maximum_budget
        or user_profile.total_budget
    )

    if (
        accommodation.estimated_price_per_night is None
        or budget is None
        or user_profile.duration_days is None
    ):
        return 0.5

    budget_per_night = (
        budget
        / user_profile.duration_days
    )

    ratio = (
        accommodation.estimated_price_per_night
        / budget_per_night
    )

    if ratio <= 1:
        return 1.0

    if ratio >= 3:
        return 0.2

    return max(
        0.2,
        2 - ratio,
    )

# ---------------------------------------------------------
# Hotel Quality
# ---------------------------------------------------------

def quality_score(
    accommodation: Accommodation,
) -> float:

    if accommodation.quality_score is None:
        return 0.5

    return accommodation.quality_score


# ---------------------------------------------------------
# Rating
# ---------------------------------------------------------

def rating_score(
    accommodation: Accommodation,
) -> float:

    if accommodation.rating is None:
        return 0.5

    return min(
        accommodation.rating / 5,
        1.0,
    )


# ---------------------------------------------------------
# Reviews
# ---------------------------------------------------------

def review_score(
    accommodation: Accommodation,
) -> float:

    reviews = accommodation.review_count or 0

    return min(
        reviews / 5000,
        1.0,
    )


# ---------------------------------------------------------
# Luxury Match
# ---------------------------------------------------------

def luxury_score(
    accommodation: Accommodation,
    user_profile: UserProfile,
) -> float:
    """
    Match hotel luxury level with user preference.
    """

    hotel_luxury = (
        accommodation.luxury_positioning
        or 0.5
    )

    styles = user_profile.travel_styles or []


    if "luxury" in styles:
        return hotel_luxury


    if (
        "budget" in styles
        or "backpacking" in styles
    ):
        return 1 - hotel_luxury


    return 0.5

# ---------------------------------------------------------
# Location
# ---------------------------------------------------------

def location_score(
    accommodation: Accommodation,
) -> float:

    if accommodation.location_quality_score is None:
        return 0.5

    return accommodation.location_quality_score


# ---------------------------------------------------------
# Semantic
# ---------------------------------------------------------

def semantic_score(
    accommodation: Accommodation,
    user_profile: UserProfile,
) -> float:
    """
    Placeholder.

    Phase 2:
    cosine(user_embedding,
           hotel_embedding)
    """

    return 0.5

def style_match_score(
    accommodation: Accommodation,
    user_profile: UserProfile,
) -> float:
    """
    Match accommodation tags with user travel styles.
    """

    styles = user_profile.travel_styles or []

    if not styles:
        return 0.5


    hotel_tags = set(
        accommodation.tags or []
    )

    matches = (
        hotel_tags
        &
        set(styles)
    )


    return min(
        len(matches) / len(styles),
        1.0,
    )

# ---------------------------------------------------------
# Overall
# ---------------------------------------------------------

def overall_score(
    accommodation: Accommodation,
    user_profile: UserProfile,
) -> float:
    """
    Compute final recommendation score.
    """

    score = (

        budget_score(
            accommodation,
            user_profile,
        ) * 0.30


        +

        quality_score(
            accommodation,
        ) * 0.20


        +

        rating_score(
            accommodation,
        ) * 0.10


        +

        review_score(
            accommodation,
        ) * 0.10


        +

        location_score(
            accommodation,
        ) * 0.10


        +

        luxury_score(
            accommodation,
            user_profile,
        ) * 0.10


        +

        style_match_score(
            accommodation,
            user_profile,
        ) * 0.05


        +

        semantic_score(
            accommodation,
            user_profile,
        ) * 0.05

    )


    return round(
        score,
        4,
    )
"""
Calculate an overall accommodation quality score.

The quality score is used by the recommendation engine
to rank accommodations independently of price.

Range
-----
0.0 - 1.0
"""

from app.trip_planner.domain.accommodation import Accommodation


# ---------------------------------------------------------
# Brand Tier Score
# ---------------------------------------------------------

BRAND_TIER_SCORE = {
    "budget": 0.30,
    "midscale": 0.50,
    "upscale": 0.70,
    "luxury": 0.90,
    "ultra_luxury": 1.00,
}


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def normalize_rating(
    rating: float | None,
) -> float:

    if rating is None:
        return 0.50

    return min(
        max(rating / 5.0, 0.0),
        1.0,
    )


def normalize_reviews(
    reviews: int | None,
) -> float:

    if reviews is None:
        return 0.0

    return min(
        reviews / 10000,
        1.0,
    )


def normalize_stars(
    stars: int | None,
) -> float:

    if stars is None:
        return 0.50

    return stars / 5.0


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def calculate_quality_score(
    accommodation: Accommodation,
) -> float:
    """
    Overall accommodation quality score.

    Weighted combination of:
    - Google reputation
    - Hotel classification
    - Location quality
    - Luxury positioning
    """

    rating_score = normalize_rating(
        accommodation.rating,
    )

    review_score = normalize_reviews(
        accommodation.review_count,
    )

    star_score = normalize_stars(
        accommodation.star_rating,
    )

    luxury_score = (
        accommodation.luxury_positioning
        if accommodation.luxury_positioning is not None
        else 0.50
    )

    location_score = (
        accommodation.location_quality_score
        if accommodation.location_quality_score is not None
        else 0.50
    )

    brand_score = BRAND_TIER_SCORE.get(
        accommodation.brand_tier,
        0.50,
    )

    score = (
        rating_score * 0.25
        + review_score * 0.15
        + star_score * 0.20
        + luxury_score * 0.20
        + location_score * 0.10
        + brand_score * 0.10
    )

    return round(
        min(score, 1.0),
        3,
    )
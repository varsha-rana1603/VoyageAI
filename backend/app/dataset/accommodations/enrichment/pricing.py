"""
Estimate accommodation prices using the destination cost profile
and semantic hotel features.
"""

from app.trip_planner.domain.accommodation import Accommodation


# ---------------------------------------------------------
# Price Tier
# ---------------------------------------------------------

def infer_price_tier(
    accommodation: Accommodation,
) -> str:
    """
    Infer budget / mid_range / luxury tier.
    """

    if accommodation.luxury_positioning is not None:

        if accommodation.luxury_positioning >= 0.80:
            return "luxury"

        if accommodation.luxury_positioning >= 0.45:
            return "mid_range"

        return "budget"

    stars = accommodation.star_rating or 3

    if stars >= 5:
        return "luxury"

    if stars >= 4:
        return "mid_range"

    return "budget"


# ---------------------------------------------------------
# Brand
# ---------------------------------------------------------

BRAND_MULTIPLIER = {

    "budget": 0.90,

    "midscale": 1.00,

    "upscale": 1.10,

    "luxury": 1.25,

    "ultra_luxury": 1.45,
}


# ---------------------------------------------------------
# Semantic Multiplier
# ---------------------------------------------------------

def semantic_multiplier(
    accommodation: Accommodation,
) -> float:
    """
    Calculates how expensive a hotel is relative to
    the destination average.
    """

    multiplier = 1.0

    # -----------------------------
    # Google reputation
    # -----------------------------

    rating = accommodation.rating or 4.0

    multiplier += (
        (rating - 4.0)
        * 0.08
    )

    reviews = accommodation.review_count or 0

    multiplier += (
        min(reviews / 10000, 1.0)
        * 0.10
    )

    # -----------------------------
    # Stars
    # -----------------------------

    stars = accommodation.star_rating or 3

    multiplier += (
        (stars - 3)
        * 0.05
    )

    # -----------------------------
    # Brand
    # -----------------------------

    multiplier *= BRAND_MULTIPLIER.get(
        accommodation.brand_tier,
        1.0,
    )

    # -----------------------------
    # Luxury positioning
    # -----------------------------

    if accommodation.luxury_positioning is not None:

        multiplier *= (
            0.80
            + accommodation.luxury_positioning * 0.40
        )

    # -----------------------------
    # Location
    # -----------------------------

    if accommodation.location_quality_score is not None:

        multiplier *= (
            0.90
            + accommodation.location_quality_score * 0.20
        )

    return round(
        max(
            0.70,
            min(
                multiplier,
                2.00,
            ),
        ),
        3,
    )


# ---------------------------------------------------------
# Confidence
# ---------------------------------------------------------

def confidence(
    accommodation: Accommodation,
) -> float:

    score = 0.50

    if accommodation.review_count:

        if accommodation.review_count > 5000:
            score += 0.20

        elif accommodation.review_count > 1000:
            score += 0.15

        elif accommodation.review_count > 200:
            score += 0.10

    if accommodation.star_rating:
        score += 0.10

    if accommodation.brand_name:
        score += 0.10

    if accommodation.luxury_positioning is not None:
        score += 0.05

    return round(
        min(score, 1.0),
        2,
    )


# ---------------------------------------------------------
# Estimate
# ---------------------------------------------------------

def estimate_prices(
    accommodations: list[Accommodation],
    destination,
) -> list[Accommodation]:

    daily_cost = destination.cost_profile["daily_cost"]

    currency = destination.cost_profile.get(
        "currency",
        "USD",
    )

    for accommodation in accommodations:

        accommodation.price_tier = (
            infer_price_tier(
                accommodation,
            )
        )

        base_price = (
            daily_cost[
                accommodation.price_tier
            ]["accommodation"]
        )

        accommodation.estimated_price_per_night = round(
            base_price
            * semantic_multiplier(
                accommodation,
            ),
            2,
        )

        accommodation.currency = currency

        accommodation.pricing_confidence = (
            confidence(
                accommodation,
            )
        )

        accommodation.pricing_source = (
            "semantic_destination_estimation_v2"
        )

    return accommodations
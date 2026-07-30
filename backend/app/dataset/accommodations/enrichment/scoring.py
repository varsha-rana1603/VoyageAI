from app.trip_planner.domain.accommodation import Accommodation


BRAND_LUXURY = {
    "budget": 0.20,
    "midscale": 0.40,
    "upscale": 0.70,
    "luxury": 0.90,
    "ultra_luxury": 1.00,
}

# ---------------------------------------------------------
# Score Weights
# ---------------------------------------------------------
from app.trip_planner.domain.accommodation import Accommodation


# ---------------------------------------------------------
# Brand Mapping
# ---------------------------------------------------------

BRAND_LUXURY = {
    "budget": 0.20,
    "midscale": 0.40,
    "upscale": 0.70,
    "luxury": 0.90,
    "ultra_luxury": 1.00,
}


# ---------------------------------------------------------
# Score Weights
# ---------------------------------------------------------

LUXURY_WEIGHTS = {
    "positioning": 0.40,
    "brand": 0.25,
    "stars": 0.20,
    "rating": 0.10,
    "reviews": 0.05,
}

BUSINESS_WEIGHTS = {
    "business_friendly": 0.70,
    "business_district": 0.20,
    "airport_area": 0.05,
    "luxury": 0.05,
    "best_for": 0.20,
}

FAMILY_WEIGHTS = {
    "family_friendly": 0.35,
    "pool": 0.20,
    "resort": 0.20,
    "beach": 0.10,
    "stars": 0.05,
    "best_for": 0.10,
}

ROMANTIC_WEIGHTS = {
    "spa": 0.25,
    "luxury": 0.30,
    "resort": 0.15,
    "beach": 0.10,
    "stars": 0.10,
    "best_for": 0.10,
}

WELLNESS_WEIGHTS = {
    "spa": 0.45,
    "resort": 0.15,
    "luxury": 0.20,
    "pool": 0.10,
    "best_for": 0.10,
}

BUDGET_WEIGHTS = {
    "luxury": 0.35,
    "brand": 0.25,
    "stars": 0.20,
    "hostel_bonus": 0.40,
    "apartment_bonus": 0.15,
    "best_for_bonus": 0.20,
}

def _clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 3)))


def estimate_semantic_scores(
    accommodation: Accommodation,
) -> Accommodation:

    # ---------------------------------------------------------
    # Luxury
    # ---------------------------------------------------------
    luxury = 0.0

    luxury += (
        accommodation.luxury_positioning or 0.0
    ) * LUXURY_WEIGHTS["positioning"]

    luxury += BRAND_LUXURY.get(
        accommodation.brand_tier,
        0.5,
    ) * LUXURY_WEIGHTS["brand"]

    luxury += (
        (accommodation.star_rating or 3) / 5
    ) * LUXURY_WEIGHTS["stars"]

    luxury += (
        (accommodation.rating or 4.0) / 5
    ) * LUXURY_WEIGHTS["rating"]

    luxury += (
        min(accommodation.review_count or 0, 10000) / 10000
    ) * LUXURY_WEIGHTS["reviews"]

    accommodation.luxury_score = _clamp(
        luxury,
    )

    # ---------------------------------------------------------
    # Business
    # ---------------------------------------------------------

    business = 0.0

    if accommodation.business_friendly:
        business += BUSINESS_WEIGHTS["business_friendly"]

    if accommodation.location_type == "business_district":
        business += BUSINESS_WEIGHTS["business_district"]

    if accommodation.location_type == "airport_area":
        business += BUSINESS_WEIGHTS["airport_area"]

    business += (
        accommodation.luxury_positioning or 0.0
    ) * BUSINESS_WEIGHTS["luxury"]

    if "business" in accommodation.best_for:
        business += BUSINESS_WEIGHTS["best_for"]

    accommodation.business_score = _clamp(business)
    # ---------------------------------------------------------
    # Family
    # ---------------------------------------------------------

    family = 0.0

    if accommodation.family_friendly:
        family += FAMILY_WEIGHTS["family_friendly"]

    if accommodation.pool:
        family += FAMILY_WEIGHTS["pool"]

    if accommodation.hotel_category == "resort":
        family += FAMILY_WEIGHTS["resort"]

    if accommodation.location_type == "beach_area":
        family += FAMILY_WEIGHTS["beach"]

    family += (
        (accommodation.star_rating or 3) / 5
    ) * FAMILY_WEIGHTS["stars"]

    if "family" in accommodation.best_for:
        family += FAMILY_WEIGHTS["best_for"]

    accommodation.family_score = _clamp(family)

    # ---------------------------------------------------------
    # Romantic
    # ---------------------------------------------------------

    romantic = 0.0

    if accommodation.spa:
        romantic += ROMANTIC_WEIGHTS["spa"]

    romantic += (
        accommodation.luxury_positioning or 0.0
    ) * ROMANTIC_WEIGHTS["luxury"]

    if accommodation.hotel_category == "resort":
        romantic += ROMANTIC_WEIGHTS["resort"]

    if accommodation.location_type == "beach_area":
        romantic += ROMANTIC_WEIGHTS["beach"]

    romantic += (
        (accommodation.star_rating or 3) / 5
    ) * ROMANTIC_WEIGHTS["stars"]

    if (
        "romantic" in accommodation.best_for
        or "couples" in accommodation.best_for
    ):
        romantic += ROMANTIC_WEIGHTS["best_for"]

    accommodation.romantic_score = _clamp(romantic)

    # ---------------------------------------------------------
    # Wellness
    # ---------------------------------------------------------

    wellness = 0.0

    if accommodation.spa:
        wellness += WELLNESS_WEIGHTS["spa"]

    if accommodation.hotel_category == "resort":
        wellness += WELLNESS_WEIGHTS["resort"]

    wellness += (
        accommodation.luxury_positioning or 0.0
    ) * WELLNESS_WEIGHTS["luxury"]

    if accommodation.pool:
        wellness += WELLNESS_WEIGHTS["pool"]

    if "wellness" in accommodation.best_for:
        wellness += WELLNESS_WEIGHTS["best_for"]

    accommodation.wellness_score = _clamp(wellness)

    # ---------------------------------------------------------
    # Budget
    # ---------------------------------------------------------

    budget = 1.0

    budget -= (
        accommodation.luxury_positioning or 0.0
    ) * BUDGET_WEIGHTS["luxury"]

    budget -= BRAND_LUXURY.get(
        accommodation.brand_tier,
        0.50,
    ) * BUDGET_WEIGHTS["brand"]

    budget -= (
        (accommodation.star_rating or 3) / 5
    ) * BUDGET_WEIGHTS["stars"]

    if accommodation.hotel_category == "hostel":
        budget += BUDGET_WEIGHTS["hostel_bonus"]

    if accommodation.hotel_category == "apartment":
        budget += BUDGET_WEIGHTS["apartment_bonus"]

    if "budget" in accommodation.best_for:
        budget += BUDGET_WEIGHTS["best_for_bonus"]

    accommodation.budget_score = _clamp(budget)

    return accommodation
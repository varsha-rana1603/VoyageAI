import math

from app.conversation.user_profile import UserProfile
from app.models.accommodation import Accommodation

from ..constants import FEATURE_NAMES
from ..schemas import FeatureVector
from .similarity import cosine_similarity


WALKABILITY = {
    "poor": 0.0,
    "average": 0.33,
    "good": 0.66,
    "excellent": 1.0,
}

SHOPPING = {
    "limited": 0.0,
    "moderate": 0.5,
    "excellent": 1.0,
}

NIGHTLIFE = {
    "low": 0.0,
    "medium": 0.5,
    "high": 1.0,
}


def _safe(
    value: float | None,
    default: float = 0.0,
) -> float:
    return float(value if value is not None else default)


def _binary(
    value: bool | None,
) -> float:
    return 1.0 if value else 0.0


def _budget_match(
    profile: UserProfile,
    accommodation: Accommodation,
) -> float:
    """
    Returns a score in [0,1] representing how well
    the hotel price fits the user's budget.
    """

    if (
        profile.total_budget is None
        or profile.duration_days is None
        or accommodation.estimated_price_per_night is None
    ):
        return 0.5

    budget_per_night = (
        profile.total_budget
        / profile.duration_days
    )

    ratio = (
        accommodation.estimated_price_per_night
        / budget_per_night
    )

    if ratio <= 1:
        return 1.0

    return max(
        0.0,
        1 - min(ratio - 1, 1),
    )


def build_feature_vector(
    profile: UserProfile,
    accommodation: Accommodation,
    user_embedding: list[float],
) -> FeatureVector:

    semantic_similarity = cosine_similarity(
        user_embedding,
        accommodation.accommodation_embedding,
    )

    metadata = accommodation.planner_metadata or {}

    features = [

        # =====================================================
        # USER FEATURES
        # =====================================================

        math.log1p(profile.total_budget or 0),

        _safe(profile.duration_days),

        _safe(profile.adults),

        _safe(profile.children),

        _binary(profile.is_family),

        _binary(profile.is_couple),

        _binary(profile.is_solo),

        _binary(profile.is_business),

        # =====================================================
        # HOTEL FEATURES
        # =====================================================

        math.log1p(
            accommodation.estimated_price_per_night or 0
        ),

        _safe(accommodation.rating),

        math.log1p(
            accommodation.review_count or 0
        ),

        _safe(accommodation.star_rating),

        _safe(accommodation.quality_score),

        _safe(accommodation.luxury_score),

        _safe(accommodation.business_score),

        _safe(accommodation.family_score),

        _safe(accommodation.romantic_score),

        _safe(accommodation.wellness_score),

        _safe(accommodation.budget_score),

        # Distance

        _safe(
            accommodation.distance_from_city_center_km
        ),

        # Amenities

        _binary(accommodation.pool),

        _binary(accommodation.spa),

        _binary(accommodation.family_friendly),

        _binary(accommodation.business_friendly),

        # =====================================================
        # LOCATION FEATURES
        # =====================================================

        WALKABILITY.get(
            metadata.get("walkability"),
            0.5,
        ),

        SHOPPING.get(
            metadata.get("shopping"),
            0.5,
        ),

        NIGHTLIFE.get(
            metadata.get("nightlife"),
            0.5,
        ),

        _binary(
            metadata.get("waterfront"),
        ),

        _safe(
            metadata.get("poi_density"),
        ),

        # =====================================================
        # INTERACTION FEATURES
        # =====================================================

        _budget_match(
            profile,
            accommodation,
        ),

        _binary(profile.is_family)
        * _safe(accommodation.family_score),

        _binary(profile.is_business)
        * _safe(accommodation.business_score),

        _binary(profile.is_couple)
        * _safe(accommodation.romantic_score),

        _binary(profile.is_solo)
        * _safe(accommodation.budget_score),

        _binary(profile.is_family)
        * _safe(accommodation.wellness_score),

        _binary(profile.is_couple)
        * _safe(accommodation.wellness_score),

        (
            1.0
            if "luxury"
            in (profile.travel_styles or [])
            else 0.0
        )
        * _safe(accommodation.luxury_score),

        # =====================================================
        # EMBEDDING FEATURE
        # =====================================================

        semantic_similarity,
    ]

    # print(f"Features: {len(features)}")
    # print(f"Feature names: {len(FEATURE_NAMES)}")

    assert len(features) == len(FEATURE_NAMES)
    return FeatureVector(features)
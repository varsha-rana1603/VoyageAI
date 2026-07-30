#Given a user profile and a hotel, how suitable is this hotel? 
#return a float in [0,1]

from app.conversation.user_profile import UserProfile
from app.models.accommodation import Accommodation

def _clamp(value: float) -> float: 
    return max(0.0, min(1.0, value))

def generate_target_score(profile: UserProfile, accommodation: Accommodation) -> float: 
    #Synthetic supervision signal
    score = 0.0
    #QUALITY
    score += 0.20 * (accommodation.quality_score or 0)
    #USER INTENT
    if profile.is_business:
        score += 0.20 * (
            accommodation.business_score or 0
        )
    if profile.is_family:
        score += 0.20 * (
            accommodation.family_score or 0
        )
    if profile.is_couple:
        score += 0.20 * (
            accommodation.romantic_score or 0
        )
    if profile.is_solo:
        score += 0.10 * (
            accommodation.budget_score or 0
        )
    #TRAVEL STYLE
    styles = profile.travel_styles or []

    if "luxury" in styles:
        score += 0.15 * (
            accommodation.luxury_score or 0
        )

    if "wellness" in styles:
        score += 0.15 * (
            accommodation.wellness_score or 0
        )

    if "budget" in styles:
        score += 0.15 * (
            accommodation.budget_score or 0
        )
    #BUDGET FIT
    if (
        profile.total_budget
        and profile.duration_days
        and accommodation.estimated_price_per_night
    ):

        budget_per_night = (
            profile.total_budget
            / profile.duration_days
        )

        ratio = (
            accommodation.estimated_price_per_night
            / budget_per_night
        )

        if ratio <= 1:
            score += 0.10
        else:
            score -= min(
                0.10,
                (ratio - 1) * 0.10,
            )

    return _clamp(score)
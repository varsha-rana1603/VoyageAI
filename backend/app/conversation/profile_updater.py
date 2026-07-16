from app.conversation.user_profile import UserProfile

from app.conversation.extractors.budget import extract_budget
from app.conversation.extractors.duration import extract_duration
from app.conversation.extractors.terrain import (
    extract_terrain_preferences,
)
from app.conversation.extractors.travel_style import (
    extract_travel_styles,
)
from app.conversation.extractors.companion_extractor import (
    extract_companions,
)
from app.conversation.extractors.month import (
    extract_travel_month,
)
from app.conversation.extractors.crowd import (
    extract_crowd_preference,
)
from app.conversation.extractors.accommodation import (
    extract_accommodation,
)
from app.conversation.extractors.lifestyle import (
    extract_lifestyle,
)


def update_profile(
    profile: UserProfile,
    message: str,
) -> UserProfile:
    """
    Updates a UserProfile using information extracted from
    the latest user message.
    """

    # ---------------------------------------
    # Budget
    # ---------------------------------------

    budget = extract_budget(message)

    if budget:

        if budget.target is not None:
            profile.total_budget = budget.target

        if budget.minimum is not None:
            profile.minimum_budget = budget.minimum

        if budget.maximum is not None:
            profile.maximum_budget = budget.maximum

    # ---------------------------------------
    # Duration
    # ---------------------------------------

    duration = extract_duration(message)

    if duration:

        if duration.target is not None:
            profile.duration_days = duration.target

        elif (
            duration.minimum is not None
            and duration.maximum is not None
        ):
            profile.duration_days = int(
                (duration.minimum + duration.maximum) / 2
            )

    # ---------------------------------------
    # Daily Budget
    # ---------------------------------------

    if (
        profile.total_budget is not None
        and profile.duration_days is not None
    ):
        profile.daily_budget = (
            profile.total_budget
            / profile.duration_days
        )

    # ---------------------------------------
    # Travel Month
    # ---------------------------------------

    month = extract_travel_month(message)

    if month:
        profile.travel_month = month.month

    # ---------------------------------------
    # Terrain
    # ---------------------------------------

    terrain = extract_terrain_preferences(message)

    if terrain:
        profile.terrain_preferences = (
            terrain.terrain_preferences
        )

    # ---------------------------------------
    # Travel Styles
    # ---------------------------------------

    styles = extract_travel_styles(message)

    if styles:
        profile.travel_styles = (
            styles.travel_styles
        )

    # ---------------------------------------
    # Crowd
    # ---------------------------------------

    crowd = extract_crowd_preference(message)

    if crowd:
        profile.crowd_preference = crowd.crowd

    # ---------------------------------------
    # Accommodation
    # ---------------------------------------

    accommodation = extract_accommodation(message)

    if accommodation:
        profile.accommodation_type = (
            accommodation.accommodation
        )

    # ---------------------------------------
    # Companions
    # ---------------------------------------

    companions = extract_companions(message)

    if companions:

        if companions.traveller_count is not None:
            profile.traveller_count = (
                companions.traveller_count
            )

        if companions.adults is not None:
            profile.adults = companions.adults

        if companions.children is not None:
            profile.children = companions.children

        profile.is_solo = companions.is_solo
        profile.is_couple = companions.is_couple
        profile.is_family = companions.is_family
        profile.is_friends = companions.is_friends
        profile.is_business = companions.is_business

    # ---------------------------------------
    # Lifestyle
    # ---------------------------------------

    lifestyle = extract_lifestyle(message)

    if lifestyle:

        if lifestyle.food is not None:
            profile.food_importance = lifestyle.food

        if lifestyle.shopping is not None:
            profile.shopping_importance = (
                lifestyle.shopping
            )

        if lifestyle.nightlife is not None:
            profile.nightlife_importance = (
                lifestyle.nightlife
            )

        if lifestyle.adventure is not None:
            profile.adventure_importance = (
                lifestyle.adventure
            )

        if lifestyle.relaxation is not None:
            profile.relaxation_importance = (
                lifestyle.relaxation
            )

        if lifestyle.culture is not None:
            profile.culture_importance = (
                lifestyle.culture
            )

        if lifestyle.nature is not None:
            profile.nature_importance = (
                lifestyle.nature
            )

    # ---------------------------------------
    # Preserve original text
    # ---------------------------------------

    if profile.free_text:
        profile.free_text += " "

    profile.free_text += message

    return profile
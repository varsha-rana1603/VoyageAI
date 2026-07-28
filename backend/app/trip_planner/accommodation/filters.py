"""
Accommodation recommendation filters.

Responsibilities
----------------
✓ Remove accommodations that do not satisfy user constraints

Not responsible for
-------------------
✗ Recommendation scoring
✗ Ranking
✗ Database queries
"""

from app.trip_planner.domain.accommodation import Accommodation
from app.conversation.user_profile import UserProfile


# ---------------------------------------------------------
# Budget Filter
# ---------------------------------------------------------

def budget_filter(
    accommodations: list[Accommodation],
    user_profile: UserProfile,
) -> list[Accommodation]:
    """
    Remove accommodations that are significantly
    above the user's accommodation budget.

    Allows a 20% tolerance.
    """

    if user_profile.maximum_budget is None:
        return accommodations

    budget_per_night = (
        user_profile.maximum_budget
        / user_profile.duration_days
    )

    max_price = budget_per_night * 1.20

    return [
        accommodation
        for accommodation in accommodations
        if (
            accommodation.estimated_price_per_night is None
            or accommodation.estimated_price_per_night <= max_price
        )
    ]


# ---------------------------------------------------------
# Traveller Type Filter
# ---------------------------------------------------------

def traveller_filter(
    accommodations: list[Accommodation],
    user_profile: UserProfile,
) -> list[Accommodation]:
    """
    Remove clearly unsuitable accommodation types.
    """

    filtered = []

    for accommodation in accommodations:

        # Families generally shouldn't stay in hostels.
        if (
            user_profile.is_family
            and accommodation.hotel_category == "hostel"
        ):
            continue

        # Business travelers generally shouldn't stay in hostels.
        if (
            user_profile.is_business
            and accommodation.hotel_category == "hostel"
        ):
            continue

        filtered.append(accommodation)

    return filtered


# ---------------------------------------------------------
# Accommodation Type Preference
# ---------------------------------------------------------

def accommodation_type_filter(
    accommodations: list[Accommodation],
    user_profile: UserProfile,
) -> list[Accommodation]:
    """
    Filter by preferred accommodation type if specified.
    """

    preferred = user_profile.accommodation_type

    if preferred is None:
        return accommodations

    filtered = [
        accommodation
        for accommodation in accommodations
        if accommodation.hotel_category == preferred
    ]

    # If nothing matches, don't eliminate all candidates.
    return filtered if filtered else accommodations


# ---------------------------------------------------------
# Main Filter Pipeline
# ---------------------------------------------------------

def filter_accommodations(
    accommodations: list[Accommodation],
    user_profile: UserProfile,
) -> list[Accommodation]:
    """
    Apply all hard filters.
    """

    accommodations = budget_filter(
        accommodations,
        user_profile,
    )

    accommodations = traveller_filter(
        accommodations,
        user_profile,
    )

    accommodations = accommodation_type_filter(
        accommodations,
        user_profile,
    )

    return accommodations
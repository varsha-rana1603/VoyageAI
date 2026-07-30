import random

from app.conversation.user_profile import UserProfile


TRAVEL_STYLES = [
    "luxury",
    "budget",
    "nature",
    "romantic",
    "family",
    "business",
    "wellness",
]

CROWD = [
    "low",
    "medium",
    "high",
]


def random_profile() -> UserProfile:

    duration = random.randint(2, 12)

    return UserProfile(

        total_budget=random.randint(
            25000,
            250000,
        ),

        duration_days=duration,

        adults=random.randint(1, 4),

        children=random.choice([0, 0, 0, 1, 2]),

        is_family=random.random() < 0.25,

        is_couple=random.random() < 0.30,

        is_business=random.random() < 0.20,

        is_solo=random.random() < 0.25,

        travel_styles=random.sample(
            TRAVEL_STYLES,
            k=random.randint(1, 3),
        ),

        crowd_preference=random.choice(
            CROWD,
        ),
    )


def generate_random_profiles(
    count: int,
) -> list[UserProfile]:
    """
    Generate a list of random user profiles.
    """

    return [
        random_profile()
        for _ in range(count)
    ]
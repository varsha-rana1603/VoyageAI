from dataclasses import dataclass


@dataclass
class LifestylePreference:

    food: int | None = None

    shopping: int | None = None

    nightlife: int | None = None

    adventure: int | None = None

    relaxation: int | None = None

    culture: int | None = None

    nature: int | None = None

    import re

from app.conversation.extractors.lifestyle import LifestylePreference


INTENSITY = {

    "love": 10,
    "adore": 10,
    "favorite": 10,

    "really like": 8,
    "enjoy": 8,

    "like": 7,

    "prefer": 7,

    "don't care": 2,
    "avoid": 1,
    "hate": 0,
}


CATEGORIES = {

    "food": {
        "food",
        "cuisine",
        "restaurants",
    },

    "shopping": {
        "shopping",
        "mall",
        "markets",
    },

    "nightlife": {
        "nightlife",
        "clubs",
        "party",
        "bars",
    },

    "adventure": {
        "adventure",
        "trek",
        "hiking",
        "rafting",
    },

    "nature": {
        "nature",
        "wildlife",
        "forest",
        "mountains",
    },

    "culture": {
        "culture",
        "history",
        "museum",
        "temple",
    },

    "relaxation": {
        "relax",
        "spa",
        "peaceful",
        "beach",
    },
}


def extract_lifestyle(
    message: str,
) -> LifestylePreference | None:

    text = message.lower()

    result = LifestylePreference()

    found = False

    for category, keywords in CATEGORIES.items():

        if any(keyword in text for keyword in keywords):

            found = True

            score = 5

            for phrase, value in INTENSITY.items():

                if phrase in text:
                    score = value
                    break

            setattr(
                result,
                category,
                score,
            )

    if not found:
        return None

    return result
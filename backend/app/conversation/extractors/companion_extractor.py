from dataclasses import dataclass
import re
from app.conversation.extractors.terrain import normalize

@dataclass
class CompanionPreference:

    traveller_count: int | None = None

    adults: int | None = None
    children: int |None = None

    is_solo: bool = False
    is_couple: bool = False
    is_family: bool = False
    is_friends: bool = False
    is_business: bool = False


NUMBER_WORDS = {
    "one":1,
    "two":2,
    "three":3,
    "four":4,
    "five":5,
    "six":6,
    "seven":7,
    "eight":8,
    "nine":9,
    "ten":10,
}


ADULT_WORDS = {
    "adult",
    "adults"
}

CHILD_WORDS = {
    "child",
    "children",
    "kid",
    "kids",
    "son",
    "daughter",
}

FRIEND_WORDS = {
    "friend",
    "friends",
    "buddy",
    "buddies",
    "gang",
}

COUPLE_WORDS = {
    "wife",
    "husband",
    "girlfriend",
    "boyfriend",
    "partner",
    "fiance",
    "fiancée",
    "couple",
    "honeymoon",
}

FAMILY_WORDS = {
    "family",
    "parents",
    "parent",
    "mother",
    "father",
    "mom",
    "dad",
    "brother",
    "sister",
}

BUSINESS_WORDS = {
    "business",
    "office",
    "work",
    "conference",
    "client",
}

COMPANION_GROUPS = {
    "couple": COUPLE_WORDS,
    "family": FAMILY_WORDS,
    "friends": FRIEND_WORDS,
    "business": BUSINESS_WORDS,
}


def contains_keywords(
    text: str,
    keywords: set[str],
) -> bool:

    normalized = normalize(text)

    keyword_stems = {
        normalize(keyword).pop()
        for keyword in keywords
    }

    return bool(normalized & keyword_stems)

def extract_companions(
    message: str,
) -> CompanionPreference | None:

    text = message.lower()

    preference = CompanionPreference()

    if any(
        word in text
        for word in {
            "solo",
            "alone",
            "myself",
            "just me",
        }
    ):
        preference.is_solo = True
        preference.traveller_count = 1
        preference.adults = 1

    preference.is_couple = contains_keywords(
        text,
        COUPLE_WORDS,
    )

    preference.is_family = contains_keywords(
        text,
        FAMILY_WORDS,
    )

    preference.is_friends = contains_keywords(
        text,
        FRIEND_WORDS,
    )

    preference.is_business = contains_keywords(
        text,
        BUSINESS_WORDS,
    )

    # -------------------------
    # Numeric traveller count
    # -------------------------

    match = re.search(
        r"\b(\d+)\s+(?:people|persons|travellers|travelers|adults?)",
        text,
    )

    if match:
        preference.traveller_count = int(match.group(1))

    # "five friends"

    if preference.traveller_count is None:

        match = re.search(
            r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\b",
            text,
        )

        if match:
            preference.traveller_count = NUMBER_WORDS[
                match.group(1)
            ]

    # -------------------------
    # Adults
    # -------------------------

    match = re.search(
        r"(\d+)\s+adults?",
        text,
    )

    if match:
        preference.adults = int(match.group(1))

    # -------------------------
    # Children
    # -------------------------

    match = re.search(
        r"(\d+)\s+(?:kids?|children)",
        text,
    )

    if match:
        preference.children = int(match.group(1))

    # -------------------------
    # Infer common cases
    # -------------------------

    if preference.is_couple:

        preference.adults = preference.adults or 2

        if preference.children is None:
            preference.traveller_count = (
                preference.traveller_count
                or 2
            )

    if preference.is_family:

        if (
            preference.adults is not None
            and
            preference.children is not None
        ):
            preference.traveller_count = (
                preference.adults
                + preference.children
            )

    if (
        not preference.is_solo
        and
        not preference.is_couple
        and
        not preference.is_family
        and
        not preference.is_friends
        and
        not preference.is_business
        and
        preference.traveller_count is None
    ):
        return None

    return preference
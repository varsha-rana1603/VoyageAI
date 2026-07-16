import re
from dataclasses import dataclass


@dataclass
class BudgetPreference:
    minimum: int | None = None
    maximum: int | None = None
    target: int | None = None

LAKH_UNITS = {"lakh", "lakhs", "lac", "lacs"}


def parse_amount(value: str, unit: str |None) -> int:
    value = float(value)

    if unit in LAKH_UNITS:
        return int(value * 100000)

    if unit == "k":
        return int(value * 1000)

    return int(value)


def extract_budget(message: str) -> BudgetPreference | None:

    text = (
        message.lower()
        .replace(",", "")
        .replace("₹", "")
        .strip()
    )

    # ----------------------------
    # Budget ranges
    # ----------------------------

    range_patterns = [

        r"(?:between|from)?\s*(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|lacs|k)?\s*(?:and|to|-)\s*(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|lacs|k)?",

        r"(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|lacs|k)?\s*-\s*(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|lacs|k)?",
    ]

    for pattern in range_patterns:

        match = re.search(pattern, text)

        if match:

            value1, unit1, value2, unit2 = match.groups()

            # If only one side has a unit, inherit it.
            if unit1 is None and unit2 is not None:
                unit1 = unit2

            if unit2 is None and unit1 is not None:
                unit2 = unit1

            return BudgetPreference(
                minimum=parse_amount(value1, unit1),
                maximum=parse_amount(value2, unit2),
            )

    # ----------------------------
    # Minimum
    # ----------------------------

    match = re.search(
        r"(?:minimum|min|at least|above|more than)\s+(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|lacs|k)?",
        text,
    )

    if match:
        return BudgetPreference(
            minimum=parse_amount(match.group(1), match.group(2))
        )

    # ----------------------------
    # Maximum
    # ----------------------------

    match = re.search(
        r"(?:maximum|max|under|below|less than|not more than|upto|up to)\s+(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|lacs|k)?",
        text,
    )

    if match:
        return BudgetPreference(
            maximum=parse_amount(match.group(1), match.group(2))
        )

    # ----------------------------
    # Approximate budget
    # ----------------------------

    match = re.search(
        r"(?:around|about|roughly|approximately)?\s*(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|lacs|k)",
        text,
    )

    if match:
        return BudgetPreference(
            target=parse_amount(match.group(1), match.group(2))
        )

    # ----------------------------
    # Plain INR value
    # ----------------------------

    match = re.search(r"\b(\d{5,8})\b", text)

    if match:
        return BudgetPreference(
            target=int(match.group(1))
        )

    return None
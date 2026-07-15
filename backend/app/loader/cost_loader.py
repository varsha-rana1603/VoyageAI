from datetime import datetime, timezone
from typing import Any

from app.loader.providers.llm_destination_provider import (
    generate_destination_profile,
)


class DestinationLoaderError(Exception):
    """Raised when a destination profile cannot be generated."""
    pass


REQUIRED_TIERS = (
    "budget",
    "mid_range",
    "luxury",
)

REQUIRED_FIELDS = (
    "accommodation",
    "food",
    "transport",
    "activities",
    "misc",
)

REQUIRED_METADATA = (
    "terrain",
    "travel_styles",
    "crowd_level",
)


def calculate_total(
    breakdown: dict[str, float]
) -> float:
    return float(sum(breakdown.values()))


def build_daily_profile(
    raw_daily_cost: dict[str, dict[str, float]]
) -> dict[str, dict[str, float]]:

    daily_cost: dict[str, dict[str, float]] = {}

    for tier in REQUIRED_TIERS:

        if tier not in raw_daily_cost:
            raise DestinationLoaderError(
                f"Missing '{tier}' cost profile."
            )

        profile = raw_daily_cost[tier].copy()

        missing_fields = [
            field
            for field in REQUIRED_FIELDS
            if field not in profile
        ]

        if missing_fields:
            raise DestinationLoaderError(
                f"Missing fields for '{tier}': {', '.join(missing_fields)}"
            )

        profile["total"] = calculate_total(profile)

        daily_cost[tier] = profile

    return daily_cost


def load_destination_profile(
    city: str,
    country: str,
) -> dict[str, Any]:
    """
    Generates and validates the complete destination profile
    using the LLM.
    """

    try:

        profile = generate_destination_profile(
            city=city,
            country=country,
        )

    except Exception as e:

        raise DestinationLoaderError(
            f"Failed generating destination profile for "
            f"{city}, {country}: {e}"
        ) from e

    # ----------------------------
    # Validate top-level keys
    # ----------------------------

    required_keys = (
        "currency",
        "daily_cost",
        "metadata",
    )

    missing = [
        key
        for key in required_keys
        if key not in profile
    ]

    if missing:
        raise DestinationLoaderError(
            f"Provider response missing keys: "
            f"{', '.join(missing)}"
        )

    # ----------------------------
    # Validate metadata
    # ----------------------------

    metadata = profile["metadata"]

    missing = [
        key
        for key in REQUIRED_METADATA
        if key not in metadata
    ]

    if missing:
        raise DestinationLoaderError(
            f"Provider metadata missing keys: "
            f"{', '.join(missing)}"
        )

    # ----------------------------
    # Validate cost profile
    # ----------------------------

    profile["daily_cost"] = build_daily_profile(
        profile["daily_cost"]
    )

    return {

        "currency": profile["currency"],

        "daily_cost": profile["daily_cost"],

        "metadata": metadata,

        "source": "Amazon Nova Lite",

        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }
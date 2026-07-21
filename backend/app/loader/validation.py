from typing import Any


def _require(data: dict[str, Any], field: str) -> None:
    """
    Raises an error if a required field is missing or empty.
    """

    value = data.get(field)

    if value is None:
        raise ValueError(f"Missing required field: {field}")

    if isinstance(value, str) and not value.strip():
        raise ValueError(f"Empty required field: {field}")


# ----------------------------------------------------
# Google Places
# ----------------------------------------------------

def validate_place(place: dict) -> None:

    required = [
        "google_place_id",
        "name",
        "country",
        "latitude",
        "longitude",
    ]

    for field in required:
        _require(place, field)


# ----------------------------------------------------
# Climate
# ----------------------------------------------------

def validate_climate(climate: dict) -> None:

    _require(climate, "best_season")

    # worst season is optional


# ----------------------------------------------------
# Metadata
# ----------------------------------------------------

def validate_metadata(metadata: dict) -> None:

    required = [
        "description",
        "terrain",
        "travel_styles",
        "crowd_level",
    ]

    for field in required:
        _require(metadata, field)

    if not isinstance(metadata["terrain"], list):
        raise ValueError("terrain must be a list")

    if not metadata["terrain"]:
        raise ValueError("terrain cannot be empty")

    if not isinstance(metadata["travel_styles"], list):
        raise ValueError("travel_styles must be a list")

    if not metadata["travel_styles"]:
        raise ValueError("travel_styles cannot be empty")


# ----------------------------------------------------
# Cost Profile
# ----------------------------------------------------

def validate_cost_profile(cost_profile: dict) -> None:

    required = [
        "currency",
        "daily_cost",
        "source",
    ]

    for field in required:
        _require(cost_profile, field)

    if not isinstance(cost_profile["daily_cost"], dict):
        raise ValueError("daily_cost must be a dictionary")


# ----------------------------------------------------
# Embedding
# ----------------------------------------------------

def validate_embedding(embedding: list[float]) -> None:

    if embedding is None:
        raise ValueError("Embedding generation failed")

    if len(embedding) == 0:
        raise ValueError("Embedding is empty")
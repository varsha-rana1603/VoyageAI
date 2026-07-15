"""
Utility functions used across the destination data loader pipeline.

Contains:
- text normalization
- currency conversion
- safe parsing helpers
- embedding text generation
- CSV loading
- list cleanup utilities
"""

import csv
from pathlib import Path

# Text utilities
def normalize_text(
    text: str | None
) -> str:

    """
    Normalize text before storing or embedding.
    """

    if not text:
        return ""

    return (
        text
        .strip()
        .lower()
    )



def clean_list(
    values: list[str]
) -> list[str]:

    """
    Remove duplicates and empty values.
    """

    return list(
        {
            item.strip()
            for item in values
            if item and item.strip()
        }
    )




# Currency / cost utilities


def convert_to_inr(
    amount: float,
    exchange_rate: float
) -> float:

    """
    Convert foreign currency amount to INR.

    Example:
        EUR 100 * 90 = INR 9000
    """

    return round(
        amount * exchange_rate,
        2
    )



def calculate_daily_cost(
    hotel_cost: float,
    food_transport_cost: float
) -> float:

    """
    Combine hotel + food + local transport.

    Used for avg_daily_cost_inr.
    """

    return round(
        hotel_cost + food_transport_cost,
        2
    )




# Safe parsing helpers


def safe_float(
    value,
    default: float = 0.0
) -> float:

    """
    Safely convert values coming from APIs.
    """

    try:
        return float(value)

    except (TypeError, ValueError):

        return default



def safe_int(
    value,
    default: int = 0
) -> int:

    """
    Safely convert integer values.
    """

    try:
        return int(value)

    except (TypeError, ValueError):

        return default




# Embedding utilities


def build_embedding_text(
    name: str,
    country: str,
    terrain: list[str],
    travel_styles: list[str],
    best_season: str,
    worst_season: str,
    crowd_level: str,
    description: str
) -> str:

    """
    Creates consistent text representation
    before generating embeddings.

    The embedding model will search this
    semantic representation.
    """

    return f"""
Destination:
{name}

Country:
{country}

Terrain:
{", ".join(terrain)}

Travel styles:
{", ".join(travel_styles)}

Best season:
{best_season}

Worst season:
{worst_season}

Crowd level:
{crowd_level}

Description:
{description}
""".strip()




# CSV utilities


def load_destination_csv(
    filepath: str
) -> list[dict]:

    """
    Load destination seed list.

    Example CSV:

    name,country
    Interlaken,Switzerland
    Bali,Indonesia
    """

    destinations = []


    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            destinations.append(row)


    return destinations




# API response helpers


def extract_nested(
    data: dict,
    keys: list[str],
    default=None
):
    """
    Safely access nested API responses.

    Example:

    extract_nested(
        response,
        ["data","hotel","price"]
    )
    """

    current = data


    try:

        for key in keys:
            current = current[key]

        return current


    except (KeyError, TypeError):

        return default




# Geographic helpers


def round_coordinates(
    latitude: float,
    longitude: float,
    precision: int = 6
):

    """
    Prevent unnecessary coordinate differences
    during database comparisons.
    """

    return (
        round(latitude, precision),
        round(longitude, precision)
    )



# File helpers
def ensure_directory(
    path: str
):

    """
    Create directory if it doesn't exist.
    """

    Path(path).mkdir(
        parents=True,
        exist_ok=True
    )
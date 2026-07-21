import json

from pydantic import ValidationError

from app.dataset.prompt import (
    SYSTEM_PROMPT,
    build_country_prompt,
)
from app.dataset.schemas import (
    CountryDestinations,
)

from app.clients.bedrock import generate_json
from app.dataset.cache import (
    country_exists,
    save_country,
)
from app.dataset.countries import COUNTRIES



class DatasetGenerationError(Exception):
    pass


def generate_country_destinations(
    country: str,
    count: int = 30,
) -> CountryDestinations:
    """
    Generates tourist destinations for a single country.
    """

    data = generate_json(
    prompt=SYSTEM_PROMPT
    + "\n\n"
    + build_country_prompt(
        country=country,
        count=count,
        )
    )

    try:

        return CountryDestinations.model_validate(
            data
        )

    except ValidationError as e:

        raise DatasetGenerationError(
            f"Schema validation failed for {country}"
        ) from e
    

def generate_all_countries(
    count: int = 40,
):

    for country in COUNTRIES:

        if country_exists(country):
            print(f"✓ {country} already cached.")
            continue

        print(f"Generating {country}...")

        result = generate_country_destinations(
            country=country,
            count=count,
        )

        save_country(result)

        print(f"Saved {country}.")
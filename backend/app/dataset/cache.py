import json
from pathlib import Path

from app.dataset.schemas import CountryDestinations

CACHE_DIR = Path("app/dataset/cache/countries")


def _country_path(country: str) -> Path:
    filename = (
        country.lower()
        .replace(" ", "_")
        .replace("/", "_")
        + ".json"
    )

    return CACHE_DIR / filename


def country_exists(country: str) -> bool:
    return _country_path(country).exists()


def save_country(
    dataset: CountryDestinations,
) -> None:

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = _country_path(dataset.country)

    with path.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            dataset.model_dump(),
            f,
            indent=2,
            ensure_ascii=False,
        )


def load_country(
    country: str,
) -> CountryDestinations:

    path = _country_path(country)

    with path.open(
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    return CountryDestinations.model_validate(
        data
    )


def load_all_countries() -> list[CountryDestinations]:

    datasets = []

    if not CACHE_DIR.exists():
        return datasets

    for file in CACHE_DIR.glob("*.json"):

        with file.open(
            encoding="utf-8",
        ) as f:

            datasets.append(
                CountryDestinations.model_validate(
                    json.load(f)
                )
            )

    return datasets
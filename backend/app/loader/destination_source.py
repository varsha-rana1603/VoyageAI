from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DestinationSource:
    name: str
    country: str
    population: int


DATA_DIR = Path(__file__).parent.parent / "data"

MIN_POPULATION = 50000
MAX_CITIES_PER_COUNTRY = 30

ALLOWED_FEATURE_CODES = {
    "PPLC",   # Capital
    "PPLA",   # State capital
    "PPLA2",
    "PPLA3",
    "PPLA4",
    "PPL",    # Populated place
}

def load_tourist_exceptions():
    with open(
        DATA_DIR / "tourist_exceptions.txt",
        encoding = "utf-8"
    ) as f:
        return {
            line.strip().lower()
            for line in f
            if line.strip()
        }

def load_country_lookup():
    lookup = {}

    with open(
        DATA_DIR / "countryInfo.txt",
        encoding="utf-8"
    ) as f:
        for line in f:

            if line.startswith("#"):
                continue

            cols = line.rstrip().split("\t")
            lookup[cols[0]] = cols[4]

    return lookup


def iter_destinations():

    print("Looking up country from countryInfo.txt")

    tourist_exceptions = load_tourist_exceptions()
    countries = load_country_lookup()

    candidates = []

    with open(
        DATA_DIR / "cities15000.txt",
        encoding="utf-8"
    ) as f:

        for line in f:

            cols = line.rstrip().split("\t")

            feature_code = cols[7]
            population = int(cols[14])

            # Ignore unsupported feature types
            if feature_code not in ALLOWED_FEATURE_CODES:
                continue

            city_name = cols[1]

            # Capitals are always kept.
            if (
                feature_code != "PPLC"
                and population < MIN_POPULATION
                and city_name.lower() not in tourist_exceptions
            ):
                continue

            country = countries.get(cols[8], cols[8])

            candidates.append(
                DestinationSource(
                    name=city_name,
                    country=country,
                    population=population,
                )
            )

    # Highest population first
    candidates.sort(
    key=lambda destination: (
        destination.name.lower() not in tourist_exceptions,
        -destination.population,
    )
)

    country_counts = defaultdict(int)
    seen = set()

    for destination in candidates:

        key = (
            destination.name.lower(),
            destination.country,
        )

        # Skip duplicate city-country pairs
        if key in seen:
            continue

        seen.add(key)

        if (
            country_counts[destination.country]
            >= MAX_CITIES_PER_COUNTRY
        ):
            continue

        country_counts[destination.country] += 1

        yield destination


if __name__ == "__main__":

    for i, destination in enumerate(iter_destinations()):

        print(destination)

        if i == 50:
            break
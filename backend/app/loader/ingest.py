from app.dataset.cache import load_all_countries
from app.dataset.generator import generate_all_countries
from app.loader.ingestor import ingest_destinations


def main():

    print("Generating missing countries...")

    generate_all_countries(
        count=40,
    )

    print("Loading cached destinations...")

    countries = load_all_countries()

    print(f"Loaded {len(countries)} countries.")

    print("Beginning enrichment...")

    created = updated = skipped = 0

    for country_data in countries:
        

        print(f"\n=== {country_data.country} ===")

        c, u, s = ingest_destinations(
            country=country_data.country,
            destinations=country_data.destinations,
        )   

        created += c
        updated += u
        skipped += s
 
    print()
    print("=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print(f"Created : {created}")
    print(f"Updated : {updated}")
    print(f"Skipped : {skipped}")
    print("=" * 60)


if __name__ == "__main__":
    main()
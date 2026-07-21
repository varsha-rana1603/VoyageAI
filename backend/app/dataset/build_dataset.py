from app.dataset.generator import (
    generate_all_countries,
)

from app.dataset.verifier import (
    verify_dataset,
)

from app.dataset.deduplicator import (
    deduplicate_destinations,
)

from app.dataset.exporter import (
    export_destinations,
)


def main():

    print("Generating destinations...")

    generated = generate_all_countries(
        count=40,
    )

    print(
        f"Generated {len(generated)} countries."
    )

    print("Verifying destinations...")

    verified = verify_dataset(
        generated,
    )

    print(
        f"Verified {len(verified)} destinations."
    )

    print("Removing duplicates...")

    verified = deduplicate_destinations(
        verified,
    )

    print(
        f"{len(verified)} unique destinations remain."
    )

    print("Exporting CSV...")

    export_destinations(
        verified,
    )

    print("Dataset generation complete.")


if __name__ == "__main__":
    main()
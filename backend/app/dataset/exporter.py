import csv
from pathlib import Path

from app.dataset.verifier import VerifiedDestination


def export_destinations(
    destinations: list[VerifiedDestination],
    output_file: str = "data/master_destinations.csv",
) -> None:
    """
    Export verified destinations to CSV.
    """

    output_path = Path(output_file)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "name",
            "country",
            "category",
            "google_place_id",
            "latitude",
            "longitude",
        ])

        for destination in destinations:

            writer.writerow([
                destination.name,
                destination.country,
                destination.category,
                destination.google_place_id,
                destination.latitude,
                destination.longitude,
            ])

    print(
        f"Exported {len(destinations)} destinations "
        f"to {output_file}"
    )

    import csv
from pathlib import Path


def export_failed(
    failed: list[tuple[str, str, str]],
    output_file: str = "data/failed_destinations.csv",
):

    output_path = Path(output_file)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "name",
            "country",
            "reason",
        ])

        writer.writerows(failed)
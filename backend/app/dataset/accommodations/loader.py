from uuid import UUID

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.destination import Destination

from .ingestor import ingest_accommodations


def load_destination_accommodations(
    destination_id: UUID,
):

    db: Session = SessionLocal()

    try:

        destination = (
            db.query(Destination)
            .filter(
                Destination.id == destination_id,
            )
            .first()
        )

        if destination is None:
            raise ValueError(
                "Destination not found."
            )

        print("=" * 80)
        print(
            f"Accommodation Loader | {destination.name}"
        )
        print("=" * 80)

        accommodations = ingest_accommodations(
            db=db,
            destination=destination,
        )

        print("\n" + "=" * 80)
        print("INGESTION SUCCESSFUL")
        print("=" * 80)
        print(
            f"Processed {len(accommodations)} accommodations."
        )

        return accommodations

    except Exception as e:

        print("\n" + "=" * 80)
        print("INGESTION FAILED")
        print("=" * 80)
        print(e)

        raise

    finally:

        db.close()


if __name__ == "__main__":

    load_destination_accommodations(
        UUID(
            "ffd6861a-bd53-4760-983e-ca81e02190ed"
        )
    )
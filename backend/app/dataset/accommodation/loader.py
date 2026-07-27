from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.accommodation import Accommodation
from app.trip_planner.context.loaders.accommodation_loader import (
    get_destination_accommodations,
)
from app.dataset.accommodation.normalizer import (
    normalize_accommodation,
)
from app.dataset.accommodation.enrichments import (
    enrich,
)
from app.dataset.accommodation.embedding import (
    generate_accommodation_embedding,
)
from app.dataset.accommodation.repository import (
    upsert_accommodation,
)


def ingest_accommodations(
    db: Session,
    destination_id: UUID,
    destination: str,
    country: str,
    limit: int = 20,
) -> int:
    """
    Ingest accommodations for a destination into PostgreSQL.

    Pipeline:
        PostgreSQL Check
            ↓
        Google Places
            ↓
        Normalize
            ↓
        Enrich
            ↓
        Embedding
            ↓
        PostgreSQL
    """

    # Check if accommodations already exist
    existing_count = (
        db.query(func.count(Accommodation.id))
        .filter(Accommodation.destination_id == destination_id)
        .scalar()
    )

    if existing_count > 0:
        print(
            f"{existing_count} accommodations already exist for {destination}. Skipping ingestion."
        )
        return existing_count

    print("Fetching accommodations from Google Places...")

    raw_places = get_destination_accommodations(
        destination=destination,
        country=country,
        limit=limit,
    )

    print(f"Found {len(raw_places)} accommodations.")

    for place in raw_places:
        accommodation = normalize_accommodation(place)

        enrich(accommodation)

        embedding = generate_accommodation_embedding(accommodation)

        upsert_accommodation(
            db=db,
            destination_id=destination_id,
            accommodation=accommodation,
            embedding=embedding,
        )

    db.commit()

    print("Accommodation ingestion completed.")

    return len(raw_places)
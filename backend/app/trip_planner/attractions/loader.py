"""
What attractions does VoyageAI know about this destination?

Query-only: this module has no knowledge of Google Places. On a cache
miss it delegates to app.dataset.attraction_ingestor, which owns
everything Places-related. That's the boundary - if this file ever
needs to import google_places directly, something has gone wrong.
"""

from sqlalchemy.orm import Session

from app.models.attraction import Attraction as AttractionORM
from app.dataset.attractions.attraction_ingestor import ingest_attractions_for_destination


def load_attractions(
    db: Session,
    destination_id: int,
    destination: str,
    country: str,
) -> list[AttractionORM]:
    existing = (
        db.query(AttractionORM)
        .filter(AttractionORM.destination_id == destination_id)
        .all()
    )

    if existing:
        return existing

    # Cache miss - delegate to ingestion. Still synchronous for now;
    # see the NOTE in ingest_attractions_for_destination.
    return ingest_attractions_for_destination(
        db=db,
        destination_id=destination_id,
        destination=destination,
        country=country,
    )
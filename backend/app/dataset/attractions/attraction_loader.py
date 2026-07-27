from sqlalchemy.orm import Session

from app.conversation.user_profile import UserProfile
from app.dataset.attractions.attraction_ingestor import (
    ingest_attractions_for_destination,
)
from app.models.attraction import Attraction
from app.models.destination import Destination


def load_attractions(
    db: Session,
    destination: Destination,
    user_profile: UserProfile,
) -> list[Attraction]:
    """
    Returns all attractions for a destination.

    If they are not already present in the database, triggers ingestion
    from Google Places.
    """

    existing = (
        db.query(Attraction)
        .filter(
            Attraction.destination_id == destination.id
        )
        .all()
    )

    if existing:
        return existing

    return ingest_attractions_for_destination(
        db=db,
        destination=destination,
        user_profile=user_profile,
    )
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.accommodation import Accommodation as AccommodationModel
from app.trip_planner.domain.accommodation import Accommodation


def _to_model_data(
    destination_id: UUID,
    accommodation: Accommodation,
    embedding: list[float],
) -> dict:
    return {
        "destination_id": destination_id,
        "google_place_id": accommodation.google_place_id,
        "name": accommodation.name,
        "lodging_type": accommodation.lodging_type,
        "description": accommodation.description,
        "website": accommodation.website,
        "latitude": accommodation.coordinates.latitude,
        "longitude": accommodation.coordinates.longitude,
        "rating": accommodation.rating,
        "review_count": accommodation.review_count,
        "price_tier": accommodation.price_tier,
        "amenities": accommodation.amenities,
        "pool": accommodation.pool,
        "spa": accommodation.spa,
        "family_friendly": accommodation.family_friendly,
        "business_friendly": accommodation.business_friendly,
        # "photo_references": accommodation.photo_references,
        "tags": accommodation.tags,
        "planner_metadata": accommodation.planner_metadata,
        "embedding_text": accommodation.embedding_text,
        "accommodation_embedding": embedding,
    }


def upsert_accommodation(
    db: Session,
    destination_id: UUID,
    accommodation: Accommodation,
    embedding: list[float],
) -> AccommodationModel:
    """
    Insert or update an accommodation.

    Idempotent:
    - same Google Place ID -> update
    - otherwise -> insert
    """

    data = _to_model_data(
        destination_id=destination_id,
        accommodation=accommodation,
        embedding=embedding,
    )

    existing = (
        db.query(AccommodationModel)
        .filter(
            AccommodationModel.google_place_id
            == accommodation.google_place_id
        )
        .first()
    )

    if existing:
        for key, value in data.items():
            setattr(existing, key, value)

        return existing

    new_accommodation = AccommodationModel(**data)
    db.add(new_accommodation)

    return new_accommodation
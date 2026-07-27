"""
Attraction ingestion for one destination: Google Places -> normalize ->
enrich -> upsert into Postgres, keyed on google_place_id.

Mirrors app.dataset.ingestor's ingest_destinations() pattern. This is
the ONLY module allowed to call the Google Places attractions client -
trip_planner.attractions.loader calls ingest_attractions_for_destination()
below rather than touching Google Places itself.
"""

from sqlalchemy.orm import Session

from app.models.destination import Destination
from app.models.attraction import Attraction as AttractionORM
from app.conversation.user_profile import UserProfile

from app.trip_planner.domain.attraction import Attraction as AttractionDomain

from app.trip_planner.providers.places.google_places import (
    generate_search_queries,
    get_destination_attractions,
)

from app.dataset.attractions.attraction_normalizer import (
    normalize_attraction,
)
from app.dataset.attractions.attraction_enrich import (
    enrich_attractions,
)
from app.dataset.attractions.attraction_mapper import (
    domain_to_orm,
)

def upsert_attractions(
    db: Session,
    destination_id: int,
    attractions: list[AttractionDomain],
) -> list[AttractionORM]:
    """
    Enriched domain Attractions in, persisted ORM Attractions out.
    Idempotent on google_place_id.
    """
    place_ids = [a.google_place_id for a in attractions]

    existing_rows = (
        db.query(AttractionORM)
        .filter(AttractionORM.google_place_id.in_(place_ids))
        .all()
    )
    existing_by_place_id = {row.google_place_id: row for row in existing_rows}

    persisted: list[AttractionORM] = []

    for domain_attraction in attractions:
        existing = existing_by_place_id.get(domain_attraction.google_place_id)

        orm_attraction = domain_to_orm(
            domain=domain_attraction,
            destination_id=destination_id,
            existing=existing,
        )

        if existing is None:
            db.add(orm_attraction)

        persisted.append(orm_attraction)

    db.commit()

    for orm_attraction in persisted:
        db.refresh(orm_attraction)

    return persisted


def ingest_attractions_for_destination(
    db: Session,
    destination: Destination,
    user_profile: UserProfile,
) -> list[AttractionORM]:

    search_queries = generate_search_queries(user_profile)

    print("\nGenerated search queries:")
    for query in search_queries:
        print(f"  • {query}")

    places = get_destination_attractions(
    latitude=destination.latitude,
    longitude=destination.longitude,
    search_queries=search_queries,
)

    domain_attractions = [
        normalize_attraction(place)
        for place in places
    ]

    enriched = enrich_attractions(domain_attractions)

    return upsert_attractions(
        db=db,
        destination_id=destination.id,
        attractions=enriched,
    )
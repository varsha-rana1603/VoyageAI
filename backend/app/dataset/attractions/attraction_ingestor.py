"""
Attraction ingestion for one destination: Google Places -> normalize ->
enrich -> upsert into Postgres, keyed on google_place_id.

Mirrors app.dataset.ingestor's ingest_destinations() pattern. This is
the ONLY module allowed to call the Google Places attractions client -
trip_planner.attractions.loader calls ingest_attractions_for_destination()
below rather than touching Google Places itself.
"""

from sqlalchemy.orm import Session

from app.models.attraction import Attraction as AttractionORM
from app.trip_planner.domain.attraction import Attraction as AttractionDomain
from app.trip_planner.providers.places.google_places import get_destination_attractions
from app.dataset.attractions.attraction_normalizer import normalize_attraction
from app.dataset.attractions.attraction_enrich import enrich_attractions
from app.dataset.attractions.attraction_mapper import domain_to_orm


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
    destination_id: int,
    destination: str,
    country: str,
) -> list[AttractionORM]:
    """
    The single entrypoint trip_planner.attractions.loader calls on a
    cache-miss. Everything Google-Places-related is contained here -
    the loader never sees a raw place dict or the Places client.

    NOTE (open question, unresolved): this runs synchronously. A cold
    cache means the caller blocks on a live Places call + enrichment.
    Revisit if this needs to become an async job with a "data not
    ready yet" response in the meantime.
    """
    places = get_destination_attractions(destination=destination, country=country)

    domain_attractions = [normalize_attraction(place) for place in places]
    enriched = enrich_attractions(domain_attractions)

    # TODO: embedding generation goes here, reusing the existing
    # sentence-transformers pipeline from destination ingestion -
    # not written here since I haven't seen that code yet.

    return upsert_attractions(
        db=db,
        destination_id=destination_id,
        attractions=enriched,
    )
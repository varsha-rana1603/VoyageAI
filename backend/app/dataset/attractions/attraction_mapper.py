"""
Maps the domain Attraction (Pydantic, provider/enrichment-facing) to the
ORM Attraction (SQLAlchemy, persistence-facing).

This is the one place that should know about both shapes. Ingestion code
should never manually construct an ORM Attraction from a domain object.

Field mismatches this resolves:
- category (domain)      -> category (ORM)
- visit_duration_minutes (domain) -> visit_duration_minutes (ORM)
- coordinates.latitude/.longitude (domain)  -> latitude, longitude (ORM)
- estimated_ticket_price (domain, Money)    -> ticket_information (ORM, JSONB)
  -> not populated yet (per Varsha, deferred) - always passes None for now.
    TODO: once a ticket-price source exists, serialize Money -> JSONB here
    (e.g. {"amount": ..., "currency": ...}), not upstream.
- is_free (domain, after fixing the if_free typo) -> is_free (ORM) - straight passthrough
"""

from app.models.attraction import Attraction as AttractionORM
from app.trip_planner.domain.attraction import Attraction as AttractionDomain


def domain_to_orm(
    domain: AttractionDomain,
    destination_id: int,
    existing: AttractionORM | None = None,
) -> AttractionORM:
    """
    Build (or update, if `existing` is passed) an ORM Attraction from a
    domain Attraction. Passing `existing` is how ingest_attractions does
    an upsert without duplicating field-by-field assignment logic here.
    """

    orm = existing or AttractionORM()

    orm.destination_id = destination_id
    orm.google_place_id = domain.google_place_id

    orm.name = domain.name
    orm.category = domain.category
    orm.description = domain.description

    orm.latitude = domain.coordinates.latitude
    orm.longitude = domain.coordinates.longitude

    orm.rating = domain.rating
    orm.review_count = domain.review_count
    orm.popularity_score = domain.popularity_score
    orm.importance = domain.importance

    orm.visit_duration_minutes = domain.visit_duration_minutes

    # Not populated yet - see TODO above.
    orm.ticket_information = None

    orm.opening_hours = domain.opening_hours

    orm.tags = domain.tags
    orm.indoor = domain.indoor
    orm.family_friendly = domain.family_friendly
    orm.is_free = domain.is_free

    # attraction_embedding intentionally left untouched here - embedding
    # generation is a separate step in the pipeline (after enrichment,
    # before upsert), not the mapper's job.

    return orm
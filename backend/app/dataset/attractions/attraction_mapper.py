"""
Maps the domain Attraction (Pydantic, provider/enrichment-facing) to the
ORM Attraction (SQLAlchemy, persistence-facing).

This is the single translation layer between domain and database models.
"""

from app.models.attraction import Attraction as AttractionORM
from app.trip_planner.domain.attraction import Attraction as AttractionDomain


def domain_to_orm(
    domain: AttractionDomain,
    destination_id: int,
    existing: AttractionORM | None = None,
) -> AttractionORM:
    """
    Build or update an ORM Attraction from a domain Attraction.
    """

    orm = existing or AttractionORM()

    # -----------------------------
    # Identity
    # -----------------------------

    orm.destination_id = destination_id
    orm.google_place_id = domain.google_place_id


    # -----------------------------
    # Basic Information
    # -----------------------------

    orm.name = domain.name
    orm.category = domain.category
    orm.description = domain.description


    orm.latitude = domain.coordinates.latitude
    orm.longitude = domain.coordinates.longitude


    # -----------------------------
    # Google Information
    # -----------------------------

    orm.rating = domain.rating
    orm.review_count = domain.review_count
    orm.popularity_score = domain.popularity_score
    orm.importance = domain.importance


    # -----------------------------
    # Visit Information
    # -----------------------------

    orm.visit_duration_minutes = (
        domain.visit_duration_minutes
    )

    orm.opening_hours = domain.opening_hours

    orm.ticket_information = (
        None
    )


    # -----------------------------
    # Planning Metadata
    # -----------------------------

    orm.tags = domain.tags

    orm.indoor = domain.indoor

    orm.family_friendly = (
        domain.family_friendly
    )

    orm.is_free = domain.is_free


    # -----------------------------
    # Experience Intelligence
    # -----------------------------

    orm.historical_score = (
        domain.historical_score
    )

    orm.architecture_score = (
        domain.architecture_score
    )

    orm.photography_score = (
        domain.photography_score
    )

    orm.crowd_score = (
        domain.crowd_score
    )

    orm.hidden_gem_score = (
        domain.hidden_gem_score
    )


    orm.experience_tags = (
        domain.experience_tags
        or []
    )

    orm.best_visit_times = (
        domain.best_visit_times
        or []
    )

    orm.estimated_cost = (
        domain.estimated_cost
    )


    # -----------------------------
    # Embedding
    # -----------------------------

    # Generated separately after enrichment.
    # Do not overwrite here.


    return orm
"""
Fetch accommodation candidates from the database.

Responsibilities
----------------
✓ Query PostgreSQL
✓ Convert ORM -> Domain

Not responsible for
-------------------
✗ Recommendation scoring
✗ Filtering
✗ Ranking
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.accommodation import (
    Accommodation as AccommodationORM,
)

from app.trip_planner.domain.accommodation import Accommodation

from .mapper import orm_to_domains


# ---------------------------------------------------------
# Candidate Retrieval
# ---------------------------------------------------------

def fetch_candidate_accommodations(
    *,
    db: Session,
    destination_id: UUID,
) -> list[Accommodation]:
    """
    Fetch all accommodation candidates for a destination.

    Parameters
    ----------
    db
        SQLAlchemy session.

    destination_id
        Destination UUID.

    Returns
    -------
    list[Accommodation]
    """

    accommodations = (
        db.query(AccommodationORM)
        .filter(
            AccommodationORM.destination_id == destination_id,
        )
        .all()
    )

    return orm_to_domains(
        accommodations,
    )


# ---------------------------------------------------------
# Candidate Retrieval with Limit
# ---------------------------------------------------------

def fetch_candidate_accommodations_limit(
    *,
    db: Session,
    destination_id: UUID,
    limit: int,
) -> list[Accommodation]:
    """
    Fetch at most `limit` accommodations.
    Useful while testing.
    """

    accommodations = (
        db.query(AccommodationORM)
        .filter(
            AccommodationORM.destination_id == destination_id,
        )
        .limit(limit)
        .all()
    )

    return orm_to_domains(
        accommodations,
    )
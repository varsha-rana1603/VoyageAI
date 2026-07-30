"""
Accommodation ingestion pipeline.

Pipeline
--------
Google Places
      ↓
Normalize
      ↓
Enrich
      ↓
Estimate Prices
      ↓
Generate Embeddings
      ↓
Map Domain -> ORM
      ↓
Upsert Database
"""

from sqlalchemy.orm import Session

from app.clients.places_client import (
    search_nearby_accommodations,
)
from app.models.accommodation import (
    Accommodation as AccommodationORM,
)
from app.trip_planner.domain.accommodation import Accommodation

from .embeddings import embed_accommodations
from .enricher import enrich_accommodations
from .mapper import domain_to_orm
from .normalizer import normalize_accommodations
from app.dataset.accommodations.enrichment.pricing import estimate_prices
from .enrichment.location.geoapify_client import GeoapifyClient

def ingest_accommodations(
    *,
    db: Session,
    destination,
):
    """
    Ingest accommodations for a destination.
    """
    geoapify = GeoapifyClient()

    print(f"\nSearching accommodations for {destination.name}...")

    # ---------------------------------------------------------
    # Fetch from Google Places
    # ---------------------------------------------------------

    raw_results = search_nearby_accommodations(
        latitude=destination.latitude,
        longitude=destination.longitude,
    )

    print(
        f"Discovered {len(raw_results)} raw accommodations."
    )

    # ---------------------------------------------------------
    # Normalize
    # ---------------------------------------------------------

    print("\nNormalizing accommodations...")

    accommodations: list[Accommodation] = (
        normalize_accommodations(raw_results)
    )

    print(
        f"Normalized {len(accommodations)} accommodations."
    )

    # ---------------------------------------------------------
    # Enrichment
    # ---------------------------------------------------------

    print("\nEnriching accommodations...")

    accommodations = enrich_accommodations(
        accommodations,
        destination,
        geoapify
    )

    print("Enrichment complete.")

    if accommodations:
        print("\nSample enriched accommodation:\n")
        print(
            accommodations[0].model_dump(
                exclude={"embedding"},
            )
        )

    # ---------------------------------------------------------
    # Pricing
    # ---------------------------------------------------------

    print("\nEstimating prices...")

    accommodations = estimate_prices(
        accommodations,
        destination,
    )

    print("Pricing complete.")

    # ---------------------------------------------------------
    # Embeddings
    # ---------------------------------------------------------

    print("\nGenerating embeddings...")

    accommodations = embed_accommodations(
        accommodations,
    )

    print("Embeddings complete.")

    # ---------------------------------------------------------
    # Persist
    # ---------------------------------------------------------

    print("\nPersisting accommodations...")

    inserted = 0
    updated = 0

    try:

        for accommodation in accommodations:

            existing = (
                db.query(AccommodationORM)
                .filter_by(
                    google_place_id=accommodation.google_place_id,
                )
                .first()
            )

            orm = domain_to_orm(
                accommodation,
                destination.id,
                existing,
            )

            if existing is None:
                db.add(orm)
                inserted += 1
            else:
                updated += 1

        db.commit()

    except Exception:

        db.rollback()
        raise

    print(
        f"\nAccommodation ingestion complete."
    )

    print(
        f"Inserted: {inserted}"
    )

    print(
        f"Updated : {updated}"
    )

    return accommodations
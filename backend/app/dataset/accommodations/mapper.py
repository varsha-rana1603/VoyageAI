"""
Maps Accommodation domain objects to the Accommodation ORM.

Responsibilities
----------------
✓ Domain -> ORM conversion
✓ Upsert support
✓ Resolve field-name differences

Not responsible for
-------------------
✗ Price estimation
✗ Metadata enrichment
✗ Embedding generation
✗ Database writes
"""

from app.models.accommodation import Accommodation as AccommodationORM
from app.trip_planner.domain.accommodation import (
    Accommodation as AccommodationDomain,
)


def domain_to_orm(
    domain: AccommodationDomain,
    destination_id,
    existing: AccommodationORM | None = None,
) -> AccommodationORM:
    """
    Build (or update) an ORM Accommodation from a domain Accommodation.
    """

    orm = existing or AccommodationORM()

    # ---------------------------------------------------------
    # Identity
    # ---------------------------------------------------------

    orm.destination_id = destination_id
    orm.google_place_id = domain.google_place_id

    # ---------------------------------------------------------
    # Basic Information
    # ---------------------------------------------------------

    orm.name = domain.name
    orm.lodging_type = domain.lodging_type
    orm.description = domain.description
    orm.website = domain.website

    orm.latitude = domain.coordinates.latitude
    orm.longitude = domain.coordinates.longitude

    # ---------------------------------------------------------
    # Google Signals
    # ---------------------------------------------------------

    orm.rating = domain.rating
    orm.review_count = domain.review_count
    orm.star_rating = domain.star_rating

    # ---------------------------------------------------------
    # AI Enrichment
    # ---------------------------------------------------------

    orm.brand_name = domain.brand_name
    orm.brand_tier = domain.brand_tier
    orm.hotel_category = domain.hotel_category

    orm.luxury_positioning = domain.luxury_positioning

    orm.location_type = domain.location_type
    orm.location_quality_score = (
        domain.location_quality_score
    )

    orm.quality_score = domain.quality_score

    orm.semantic_features = (
        domain.semantic_features
    )

    orm.enrichment_confidence = (
        domain.enrichment_confidence
    )

    orm.enrichment_source = (
        domain.enrichment_source
    )

    # ---------------------------------------------------------
    # Pricing
    # ---------------------------------------------------------

    orm.estimated_price_per_night = (
        domain.estimated_price_per_night
    )

    orm.currency = domain.currency

    orm.price_confidence = (
        domain.pricing_confidence
    )

    metadata = orm.metadata_json or {}

    metadata.update(
        {
            "pricing_source": domain.pricing_source,
            "price_tier": domain.price_tier,
        }
    )

    orm.metadata_json = metadata

    # ---------------------------------------------------------
    # Location Intelligence
    # ---------------------------------------------------------

    orm.distance_from_city_center_km = (
        domain.distance_to_city_center_km
    )

    orm.distance_to_metro_m = (
        domain.distance_to_nearest_metro_km
    )

    # Computed later by the planner
    orm.distance_to_main_attractions_km = None
    orm.average_travel_time_minutes = None

    # ---------------------------------------------------------
    # Amenities
    # ---------------------------------------------------------

    orm.amenities = domain.amenities
    orm.tags = domain.tags
    orm.best_for = domain.best_for

    orm.pool = domain.pool
    orm.spa = domain.spa

    orm.family_friendly = (
        domain.family_friendly
    )

    orm.business_friendly = (
        domain.business_friendly
    )

    # ---------------------------------------------------------
    # Planner Metadata
    # ---------------------------------------------------------

    orm.planner_metadata = (
        domain.planner_metadata
    )

    # ---------------------------------------------------------
    # Photos
    # ---------------------------------------------------------

    orm.photos = None

    # ---------------------------------------------------------
    # AI Embeddings
    # ---------------------------------------------------------

    orm.embedding_text = (
        domain.embedding_text
    )

    orm.accommodation_embedding = (
        domain.embedding
    )

    return orm
"""
Maps Accommodation ORM models into Accommodation domain models.
"""

from app.models.accommodation import (
    Accommodation as AccommodationORM,
)

from app.trip_planner.domain.accommodation import Accommodation
from app.trip_planner.domain.common import Coordinates


def orm_to_domain(
    orm: AccommodationORM,
) -> Accommodation:
    """
    Convert one Accommodation ORM object into
    the domain Accommodation model.
    """

    return Accommodation(

        # ---------------------------------------------------------
        # Identity
        # ---------------------------------------------------------

        name=orm.name,
        google_place_id=orm.google_place_id,

        coordinates=Coordinates(
            latitude=orm.latitude,
            longitude=orm.longitude,
        ),

        # ---------------------------------------------------------
        # Basic Information
        # ---------------------------------------------------------

        lodging_type=orm.lodging_type,
        description=orm.description,
        website=orm.website,

        # ---------------------------------------------------------
        # Google Signals
        # ---------------------------------------------------------

        rating=orm.rating,
        review_count=orm.review_count,

        # ---------------------------------------------------------
        # Pricing
        # ---------------------------------------------------------

        estimated_price_per_night=orm.estimated_price_per_night,
        currency=orm.currency,

        pricing_source=(
            orm.metadata_json.get("pricing_source")
            if orm.metadata_json
            else None
        ),

        pricing_confidence=orm.pricing_confidence,

        price_tier=(
            orm.metadata_json.get("price_tier")
            if orm.metadata_json
            else None
        ),

        # ---------------------------------------------------------
        # Amenities
        # ---------------------------------------------------------

        amenities=orm.amenities or [],

        pool=orm.pool,
        spa=orm.spa,

        family_friendly=orm.family_friendly,
        business_friendly=orm.business_friendly,

        # ---------------------------------------------------------
        # Planner Metadata
        # ---------------------------------------------------------

        tags=orm.tags or [],

        star_rating=orm.star_rating,

        best_for=orm.best_for or [],

        distance_to_city_center_km=(
            orm.distance_from_city_center_km
        ),

        distance_to_nearest_metro_km=(
            orm.distance_to_metro_m
        ),

        planner_metadata=(
            orm.planner_metadata or {}
        ),

        # ---------------------------------------------------------
        # AI
        # ---------------------------------------------------------

        embedding_text=orm.embedding_text,
        embedding=orm.accommodation_embedding,

        # ---------------------------------------------------------
        # AI Enrichment
        # ---------------------------------------------------------

        brand_name=orm.brand_name,
        brand_tier=orm.brand_tier,
        hotel_category=orm.hotel_category,

        luxury_positioning=orm.luxury_positioning,

        location_type=orm.location_type,
        location_quality_score=(
            orm.location_quality_score
        ),

        quality_score=orm.quality_score,

        semantic_features=(
            orm.semantic_features or {}
        ),

        enrichment_confidence=(
            orm.enrichment_confidence
        ),

        enrichment_source=(
            orm.enrichment_source
        ),
    )


def orm_to_domains(
    accommodations: list[AccommodationORM],
) -> list[Accommodation]:
    """
    Convert a collection of ORM accommodations
    into domain accommodations.
    """

    return [
        orm_to_domain(accommodation)
        for accommodation in accommodations
    ]
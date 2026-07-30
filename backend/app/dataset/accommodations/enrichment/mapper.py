from app.trip_planner.domain.accommodation import Accommodation

from .schemas import HotelSemanticFeatures


def apply_semantic_features(
    accommodation: Accommodation,
    features: HotelSemanticFeatures,
):

    accommodation.brand_name = (
        features.brand_name
    )

    accommodation.brand_tier = (
        features.brand_tier
    )

    accommodation.hotel_category = (
        features.hotel_category
    )

    if accommodation.star_rating is None:
        accommodation.star_rating = (
            features.estimated_stars
        )

    accommodation.luxury_positioning = (
        features.luxury_positioning
    )

    accommodation.location_type = (
        features.location_type
    )

    accommodation.location_quality_score = (
        features.location_quality_score
    )


    # Amenities

    accommodation.pool = (
        features.pool
    )

    accommodation.spa = (
        features.spa
    )


    # Traveller suitability

    accommodation.business_friendly = (
        features.business_friendly
    )

    accommodation.family_friendly = (
        features.family_friendly
    )


    accommodation.best_for = (
        features.best_for
    )


    accommodation.semantic_features = (
        features.model_dump()
    )

    accommodation.enrichment_source = (
        "amazon_nova_lite"
    )

    return accommodation
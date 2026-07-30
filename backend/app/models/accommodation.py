import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.config import settings
from app.database import Base


class Accommodation(Base):
    __tablename__ = "accommodations"

    # --------------------------------------------------
    # Identity
    # --------------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
    )

    destination_id = Column(
        UUID(as_uuid=True),
        ForeignKey("destinations.id"),
        nullable=False,
        index=True,
    )

    google_place_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    # --------------------------------------------------
    # Basic Information
    # --------------------------------------------------

    name = Column(
        String,
        nullable=False,
    )

    lodging_type = Column(
        String,
    )

    description = Column(
        String,
    )

    website = Column(
        String,
    )

    latitude = Column(
        Float,
        nullable=False,
    )

    longitude = Column(
        Float,
        nullable=False,
    )

    # --------------------------------------------------
    # Google Signals
    # --------------------------------------------------

    rating = Column(
        Float,
    )

    review_count = Column(
        Integer,
    )

    star_rating = Column(
        Integer,
    )

    # --------------------------------------------------
    # AI Enrichment
    # --------------------------------------------------

    brand_name = Column(
        String,
    )

    brand_tier = Column(
        String,
    )

    hotel_category = Column(
        String,
    )

    luxury_positioning = Column(
        Float,
    )

    location_type = Column(
        String,
    )

    location_quality_score = Column(
        Float,
    )

    quality_score = Column(
        Float,
    )

    # --------------------------------------------------
    # Semantic Scores
    # --------------------------------------------------

    luxury_score = Column(
        Float,
    )

    business_score = Column(
        Float,
    )

    family_score = Column(
        Float,
    )

    romantic_score = Column(
        Float,
    )

    wellness_score = Column(
        Float,
    )

    budget_score = Column(
        Float,
    )

    semantic_features = Column(
        JSONB,
    )

    enrichment_confidence = Column(
        Float,
    )

    enrichment_source = Column(
        String,
    )

    # --------------------------------------------------
    # Pricing
    # --------------------------------------------------

    estimated_price_per_night = Column(
        Float,
    )

    currency = Column(
        String,
        default="USD",
    )

    pricing_confidence = Column(
        Float,
    )

    # --------------------------------------------------
    # Location Intelligence
    # --------------------------------------------------

    distance_from_city_center_km = Column(
        Float,
    )

    distance_to_metro_m = Column(
        Float,
    )

    distance_to_main_attractions_km = Column(
        Float,
    )

    average_travel_time_minutes = Column(
        Float,
    )

    # --------------------------------------------------
    # Amenities
    # --------------------------------------------------

    amenities = Column(
        JSONB,
    )

    tags = Column(
        JSONB,
    )

    best_for = Column(
        JSONB,
    )

    pool = Column(
        Boolean,
    )

    spa = Column(
        Boolean,
    )

    family_friendly = Column(
        Boolean,
    )

    business_friendly = Column(
        Boolean,
    )

    # --------------------------------------------------
    # Images / Planner Metadata
    # --------------------------------------------------

    photos = Column(
        JSONB,
    )

    planner_metadata = Column(
        JSONB,
    )

    metadata_json = Column(
        JSONB,
    )

    # --------------------------------------------------
    # Embeddings
    # --------------------------------------------------

    embedding_text = Column(
        Text,
    )

    accommodation_embedding = Column(
        Vector(settings.embedding_dimensions),
    )

    # --------------------------------------------------
    # Audit
    # --------------------------------------------------

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # --------------------------------------------------
    # Relationships
    # --------------------------------------------------

    destination = relationship(
        "Destination",
        back_populates="accommodations",
    )
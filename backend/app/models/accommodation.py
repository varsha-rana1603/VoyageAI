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
    Text
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.config import settings


class Accommodation(Base):
    __tablename__ = "accommodations"

    # -----------------------------
    # Identity
    # -----------------------------
    id = Column(Integer, primary_key=True)

    # UUID, not Integer - destinations.id is UUID (see attractions.destination_id
    # for the bug this caused last time when this was assumed to be int).
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

    # -----------------------------
    # Basic Information
    # -----------------------------
    name = Column(String, nullable=False)

    lodging_type = Column(String)  # "hotel" | "hostel" | "guest_house" | etc

    description = Column(String)

    website = Column(String)

    latitude = Column(Float, nullable=False)

    longitude = Column(Float, nullable=False)

    # -----------------------------
    # Google Signal
    # -----------------------------
    rating = Column(Float)

    review_count = Column(Integer)

    # -----------------------------
    # Trip Planning Metadata
    # -----------------------------
    price_tier = Column(String)  # "budget" | "mid_range" | "luxury"
    tags = Column(JSONB)
    planner_metadata = Column(JSONB)

    amenities = Column(JSONB)

    pool = Column(Boolean)

    spa = Column(Boolean)

    family_friendly = Column(Boolean)

    business_friendly = Column(Boolean)

    # -----------------------------
    # AI Metadata
    # -----------------------------
    accommodation_embedding = Column(
        Vector(settings.embedding_dimensions)
    )

    metadata_json = Column(JSONB)
    embedding_text = Column(Text)

    # -----------------------------
    # Audit
    # -----------------------------
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    destination = relationship(
        "Destination",
        back_populates="accommodations",
    )
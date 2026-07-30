from datetime import datetime
import uuid
from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import (JSONB,UUID)
from sqlalchemy.orm import relationship

from app.database import Base
from app.config import settings


class Attraction(Base):
    __tablename__ = "attractions"

    # -----------------------------
    # Identity
    # -----------------------------
    id = Column(Integer, primary_key=True)

    destination_id = Column(
        UUID(as_uuid = True),
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

    category = Column(String)

    description = Column(String)

    latitude = Column(Float, nullable=False)

    longitude = Column(Float, nullable=False)

    # -----------------------------
    # Google Popularity
    # -----------------------------
    rating = Column(Float)

    review_count = Column(Integer)

    popularity_score = Column(Float)

    importance = Column(String)

    # -----------------------------
    # Visit Information
    # -----------------------------
    visit_duration_minutes = Column(Integer)

    opening_hours = Column(JSONB)

    ticket_information = Column(JSONB)

    # -----------------------------
    # Trip Planning Metadata
    # -----------------------------
    tags = Column(JSONB)

    indoor = Column(Boolean)

    family_friendly = Column(Boolean)

    is_free = Column(Boolean)

        # -----------------------------
    # Experience Intelligence
    # -----------------------------

    historical_score = Column(Float)

    architecture_score = Column(Float)

    photography_score = Column(Float)

    crowd_score = Column(Float)

    hidden_gem_score = Column(Float)


    experience_tags = Column(JSONB)

    best_visit_times = Column(JSONB)

    estimated_cost = Column(Float)

    # -----------------------------
    # AI Metadata
    # -----------------------------
    attraction_embedding = Column(
        Vector(settings.embedding_dimensions)
    )

    metadata_json = Column(JSONB)

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
        back_populates="attractions",
    )
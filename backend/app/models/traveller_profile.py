import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.database import Base


class TravellerProfile(Base):
    """
    A traveller profile is built incrementally across conversation turns.
    Fields start null and get filled in as the LLM extracts them; embedding
    is only generated once enough fields are present to make it meaningful
    (see ProfileService.is_ready_for_embedding).
    """

    __tablename__ = "traveller_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Structured preference fields, extracted from free-text conversation.
    # travel_style must match one of the canonical values in
    # app/services/profile_service.py CANONICAL_TRAVEL_STYLES -- never
    # silently coerced to a different style if extraction returns something
    # unrecognized (see profile_service.py for the explicit handling).
    travel_style: Mapped[str | None] = mapped_column(String, nullable=True)
    budget_tier: Mapped[str | None] = mapped_column(String, nullable=True)  # low | medium | high
    crowd_tolerance: Mapped[str | None] = mapped_column(String, nullable=True)  # low | medium | high
    trip_duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_conversation: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)

    profile_embedding: Mapped[list | None] = mapped_column(Vector(settings.embedding_dim), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # user = relationship("User", back_populates="profiles")
    trips = relationship("Trip", back_populates="traveller_profile", cascade="all, delete-orphan")

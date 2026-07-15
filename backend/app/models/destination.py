import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.database import Base


class Destination(Base):
    __tablename__ = "destinations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    country: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Coordinates are required, not optional -- Open-Meteo climate lookups and
    # any future distance/proximity features (Nuance 2's "1hr train to Paris")
    # need them. Sourced from Google Places, not user-entered.
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    # Real per-day spend estimate. Sourced from Amadeus average nightly hotel
    # rate + a food/local-transport heuristic (see loader) -- replaces the old
    # base_cost_inr/base_cost_duration_days split, which existed only because
    # there was no real per-day figure available yet.
    # avg_daily_cost_inr: Mapped[float] = mapped_column(Float, nullable=False)

    cost_profile: Mapped[dict] = mapped_column(
        JSONB,
        nullable = False,
        default = dict
    )

    # Derived from Open-Meteo historical climate normals, not guessed.
    best_season: Mapped[str] = mapped_column(String, nullable=False)  # e.g. "Oct-Mar"
    worst_season: Mapped[str | None] = mapped_column(String, nullable=True)  # e.g. "Jun-Aug" -- used for date filtering

    terrain: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)  # mountain | beach | forest | city | desert ...
    travel_styles: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)  # derived from Places `types`, see loader

    # userRatingCount-based proxy, not a real crowding measurement -- see
    # loader's crowd_level_from_rating_count() for the explicit caveat.
    typical_crowd_level: Mapped[str] = mapped_column(String, nullable=False)  # low | medium | high

    destination_embedding: Mapped[list | None] = mapped_column(Vector(settings.embedding_dim), nullable=True)

    # Source tracking -- lets the loader upsert idempotently instead of only
    # ever inserting, and makes stale-data refresh possible later.
    google_place_id: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    data_updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    trips = relationship("Trip", back_populates="destination")
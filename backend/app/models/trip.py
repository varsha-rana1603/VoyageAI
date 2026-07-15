import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Trip(Base):
    """
    A scored (profile, destination) pairing. One row per recommendation
    surfaced to a user -- kept so recommendations are auditable/explainable
    and, eventually, usable as training signal for a future ranking model.
    """

    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    traveller_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("traveller_profiles.id"), nullable=False
    )
    destination_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("destinations.id"), nullable=False)

    match_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-1, see app/ml/scoring.py
    estimated_cost_inr: Mapped[float] = mapped_column(Float, nullable=False)
    within_budget: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    traveller_profile = relationship("TravellerProfile", back_populates="trips")
    destination = relationship("Destination", back_populates="trips")

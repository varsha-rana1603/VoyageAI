from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    JSON,
    DateTime,
    UniqueConstraint
)

from datetime import datetime

from .database import Base

class Stay(Base):
    __tablename__ = "stays"
    __table_args__ = (
        UniqueConstraint(
            "destination",
            "name",
            name="unique_stay"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    destination = Column(
        String,
        index=True
    )
    name = Column(
        String
    )
    lat = Column(
        Float
    )
    lon = Column(
        Float
    )
    data = Column(
        JSON
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    String,
    JSON,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ConversationSession(Base):

    __tablename__ = "conversation_sessions"


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )


    status: Mapped[str] = mapped_column(
        String,
        default="collecting"
    )


    travel_profile: Mapped[dict] = mapped_column(
        JSON,
        default=dict
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


    messages = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


class ConversationMessage(Base):

    __tablename__ = "conversation_messages"


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversation_sessions.id"),
        nullable=False
    )


    role: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    # user / assistant


    content: Mapped[str] = mapped_column(
        String,
        nullable=False
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


    conversation = relationship(
        "ConversationSession",
        back_populates="messages"
    )
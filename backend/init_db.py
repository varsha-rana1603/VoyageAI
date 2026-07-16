"""
One-shot DB setup for Phase 1: enables the pgvector extension, then creates
all tables from the ORM models. Use Alembic migrations instead of this once
the schema needs to evolve without dropping data.

Run with: python init_db.py
"""
from backend.app.models import traveller_profile
from sqlalchemy import text

from app.database import Base, engine
from app.models import destination, trip, user  # noqa: F401 -- registers models on Base

def init():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    print("Database initialized: pgvector enabled, tables created.")


if __name__ == "__main__":
    init()

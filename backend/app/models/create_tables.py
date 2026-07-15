from app.database import Base, engine

# Import all models so SQLAlchemy knows about them
from app.models.destination import Destination
from app.models.trip import Trip
from app.models.user import User

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")
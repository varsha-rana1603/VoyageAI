"""
Importing every model here ensures SQLAlchemy's declarative registry has
all classes registered before any relationship() string reference (e.g.
relationship("User")) gets resolved -- otherwise whichever model happens
to get imported first triggers a KeyError/InvalidRequestError for any
sibling model it references that hasn't been imported yet.
"""
from app.models.user import User  # noqa: F401
from app.models.traveller_profile import TravellerProfile  # noqa: F401
from app.models.destination import Destination  # noqa: F401
from app.models.trip import Trip  # noqa: F401
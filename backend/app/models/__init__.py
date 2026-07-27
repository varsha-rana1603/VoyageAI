"""
Importing every model here ensures SQLAlchemy's declarative registry has
all classes registered before any relationship() string reference (e.g.
relationship("User")) gets resolved -- otherwise whichever model happens
to get imported first triggers a KeyError/InvalidRequestError for any
sibling model it references that hasn't been imported yet.
"""
from app.models.user import User
from app.models.traveller_profile import TravellerProfile
from app.models.destination import Destination
from app.models.trip import Trip
from app.models.attraction import Attraction
from app.models.accommodation import Accommodation
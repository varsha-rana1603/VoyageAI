from pydantic import BaseModel
from .attraction import Attraction
from .destination import DestinationInfo, DestinationMetadata
from .nearby import NearbyDestination

class DestinationContext(BaseModel):
    #Complete knowledge VoyageAI has about a destination
    #Immutable object; serves as input to all trip-planning modules

    destination: DestinationInfo
    metadata: DestinationMetadata
    attractions: list[Attraction]
    nearby_destinations: list[NearbyDestination]
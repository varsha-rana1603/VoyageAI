from sqlalchemy.orm import Session
from app.models.destination import Destination
from app.trip_planner.domain.common import Coordinates
from app.trip_planner.domain.destination import (DestinationInfo, DestinationMetadata)
from pydantic import BaseModel


class DestinationLoadResult(BaseModel):
    """
    Result returned by the destination loader.
    """

    info: DestinationInfo
    metadata: DestinationMetadata

def load_destination(
    db: Session,
    name: str,
    country: str,
) -> DestinationLoadResult:

    destination = (
        db.query(Destination)
        .filter(
            Destination.name == name,
            Destination.country == country,
        )
        .first()
    )

    if destination is None:
        raise ValueError(
            f"Destination '{name}, {country}' not found."
        )

    info = DestinationInfo(
        name=destination.name,
        country=destination.country,
        coordinates=Coordinates(
            latitude=destination.latitude,
            longitude=destination.longitude,
        ),
        timezone="",   # TODO: Add timezone to ingestion pipeline
        currency=destination.cost_profile["currency"],
        google_place_id=destination.google_place_id,
    )

    metadata = DestinationMetadata(
        description=destination.description,
        terrain=destination.terrain,
        travel_styles=destination.travel_styles,
        best_season=destination.best_season,
        worst_season=destination.worst_season,
        crowd_level=destination.typical_crowd_level,
        cost_profile=destination.cost_profile,
    )

    return DestinationLoadResult(
        info=info,
        metadata=metadata,
    )
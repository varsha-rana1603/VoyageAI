from app.database import SessionLocal

from app.trip_planner.context.loaders.destination_loader import (
    load_destination,
)

from app.trip_planner.domain.context import DestinationContext


class DestinationContextBuilder:

    def build(
        self,
        destination: str,
        country: str,
    ) -> DestinationContext:

        db = SessionLocal()

        try:

            result = load_destination(
                db=db,
                name=destination,
                country=country,
            )

            context = DestinationContext(
                destination=result.info,
                metadata=result.metadata,
                attractions=[],
                nearby_destinations=[],
            )

            return context

        finally:
            db.close()
#What attractions does VoyageAI know about this destination? 

from sqlalchemy.orm import Session
from app.trip_planner.domain.attraction import Attraction
from app.trip_planner.domain.common import Coordinates
from app.trip_planner.providers.places.google_places import get_destination_attractions

def normalize_attraction(place: dict) -> Attraction:
    return Attraction(
        name = place["displayName"]["text"],
        google_place_id = place["id"],
        attraction_type = place.get("types",["unknown"])[0],
        description = None,
        coordinates = Coordinates(
            latitude = place["location"]["latitude"],
            longitude = place["location"]["longitude"]
        ),
        rating = place.get("rating"),
        review_count = place.get("userRatingCount"),
        popularity_score = None,
        importance = None,
        estimated_visit_duration_minutes = None,
        estimated_ticket_price = None,
        opening_hours=(
            place.get("regularOpeningHours", {})
            .get("weekdayDescriptions", [])
        ),

        indoor=None,

        family_friendly=None,

        website=place.get("websiteUri"),

        # photo_references=[
        #     photo["name"]
        #     for photo in place.get("photos", [])
        # ],

        tags=place.get("types", []),

        is_free=None,
    )

def load_attractions(db: Session, destination: str, country: str) -> list[Attraction]:
    #Check postgreSQL first
    places = get_destination_attractions(destination = destination, country = country)

    return [
        normalize_attraction(place)
        for place in places
    ]
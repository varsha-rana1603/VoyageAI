from dataclasses import dataclass

from app.conversation.extractors.terrain import normalize


@dataclass
class AccommodationPreference:
    accommodation: str


ACCOMMODATIONS = {

    "hostel": {
        "hostel",
        "hostels",
    },

    "hotel": {
        "hotel",
        "hotels",
    },

    "luxury_hotel": {
        "luxury",
        "resort",
        "five-star",
        "5-star",
    },

    "villa": {
        "villa",
        "villas",
    },

    "apartment": {
        "apartment",
        "apartments",
        "airbnb",
    },

    "camping": {
        "camping",
        "camp",
        "tent",
    },
}


def extract_accommodation(
    message: str,
) -> AccommodationPreference | None:

    words = normalize(message)

    for label, keywords in ACCOMMODATIONS.items():

        stems = {
            normalize(keyword).pop()
            for keyword in keywords
        }

        if words & stems:
            return AccommodationPreference(label)

    return None
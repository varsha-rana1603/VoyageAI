import requests

from app.config import GEOAPIFY_API_KEY


from app.database.database import SessionLocal
from app.database.models import Stay


def fetch_nearby_places(
    lat: float,
    lon: float,
    categories: list,
    radius_m: int = 1500,
    limit: int = 50
):

    db = SessionLocal()

    cached = (
        db.query(Stay)
        .filter(
            Stay.lat == lat,
            Stay.lon == lon
        )
        .first()
    )


    if cached and cached.data.get("nearby_places"):

        print("Loaded nearby places from cache")

        places = cached.data["nearby_places"]

        db.close()

        return places


    db.close()


    print("No nearby cache. Calling Geoapify...")


    url = "https://api.geoapify.com/v2/places"


    params = {
        "categories": ",".join(categories),

        "filter":
            f"circle:{lon},{lat},{radius_m}",

        "bias":
            f"proximity:{lon},{lat}",

        "limit": limit,

        "apiKey": GEOAPIFY_API_KEY
    }


    response = requests.get(
        url,
        params=params
    )

    response.raise_for_status()


    places = [
        feature["properties"]
        for feature in response.json()["features"]
    ]


    # save cache
    db = SessionLocal()

    stay = (
        db.query(Stay)
        .filter(
            Stay.lat == lat,
            Stay.lon == lon
        )
        .first()
    )


    if stay:

        updated_data = stay.data

        updated_data["nearby_places"] = places

        stay.data = updated_data

        db.commit()


    db.close()


    return places
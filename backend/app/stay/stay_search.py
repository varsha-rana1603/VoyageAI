#fetch hotels from OpenStreetMaps using the free Overpass API

import requests
from app.config import GEOAPIFY_API_KEY
from app.stay.geocoder import geocode
from app.stay.stay_normalizer import normalize_stays
from app.stay.stay_enrichment import enrich_stays
from app.database.database import SessionLocal
from app.database.models import Stay
from sqlalchemy import func

def filter_stays(stays):

    print("BEFORE FILTER:", len(stays))

    filtered = []

    for stay in stays:

        # print("\nCHECKING:", stay)

        name = stay.get("name")

        if not name:
            print("REMOVED: no name")
            continue


        bad_names = [
            "unknown",
            "unnamed",
            "hotel",
            "n/a",
            "null",
            "-"
        ]


        if name.lower().strip() in bad_names:
            print("REMOVED: bad name", name)
            continue


        if (
            stay.get("lat") is None
            or
            stay.get("lon") is None
        ):
            print("REMOVED: no coordinates")
            continue


        if not stay.get("address"):
            print("REMOVED: no address")
            continue


        filtered.append(stay)


    print(
        "AFTER FILTER:",
        len(filtered)
    )

    return filtered

def get_cached_stays(destination_name):

    db = SessionLocal()

    stays = (
        db.query(Stay)
        .filter(
            func.lower(Stay.destination)
            ==
            destination_name.lower()
        )
        .all()
    )

    db.close()

    return [
        stay.data
        for stay in stays
    ]

def save_stays(destination_name, stays):

    db = SessionLocal()

    for stay in stays:

        db.add(
            Stay(
                destination=destination_name.lower(),
                name=stay["name"],
                lat=stay["lat"],
                lon=stay["lon"],
                data=stay
            )
        )


    db.commit()
    db.close()

    print(
        "Saved:",
        len(stays)
    )

def fetch_stay(destination_name: str, radius=20000, limit=50):

    print("Fetching from Geoapify...")


    coords = geocode(destination_name)


    url = "https://api.geoapify.com/v2/places"


    params = {
        "categories": ",".join([
            "accommodation.hotel",
            "accommodation.hostel",
            "accommodation.guest_house",
            "accommodation.apartment"
        ]),
        "filter":
            f"circle:{coords['lon']},{coords['lat']},{radius}",
        "bias":
            f"proximity:{coords['lon']},{coords['lat']}",
        "limit":limit,
        "apiKey": GEOAPIFY_API_KEY
    }


    response = requests.get(
        url,
        params=params
    )


    response.raise_for_status()

    stays = normalize_stays(
        response.json()["features"],
        coords["lat"],
        coords["lon"]
    )
    return stays
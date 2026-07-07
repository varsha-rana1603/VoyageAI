#fetch hotels from OpenStreetMaps using the free Overpass API

import requests
from app.config import GEOAPIFY_API_KEY
from app.stay.geocoder import geocode
from app.stay.stay_normalizer import normalize_stays

def fetch_stay(destination_name: str, radius=100000, limit=50):
    print("Fetching...")
    coords = geocode(destination_name)

    url = "https://api.geoapify.com/v2/places"

    params = {
        "categories":",".join([
            "accommodation.hotel",
            "accommodation.hostel",
            "accommodation.guest_house",
            "accommodation.apartment"
        ]),
        "filter": f"circle:{coords['lon']},{coords['lat']},{radius}",
        "bias": f"proximity:{coords['lon']},{coords['lat']}",
        "limit": limit,
        "apiKey": GEOAPIFY_API_KEY  
    }

    response = requests.get(url,params=params)
    response.raise_for_status()

    stays = response.json()['features']
    print("Stays",len(stays))
    return normalize_stays(
        stays,
        coords['lat'],
        coords['lon']
    )

if __name__ == "__main__":
    stays = fetch_stay("Bangalore")
    print(f"Found {len(stays)} stays\n")

    for stay in stays:
        print("----------------")
        print(stay["name"])
        print(stay["address"])
        print(stay["categories"])
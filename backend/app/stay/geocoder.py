import requests

from ..config import GEOAPIFY_API_KEY


def geocode(place_name: str):

    url = "https://api.geoapify.com/v1/geocode/search"

    params = {
        "text": place_name,
        "apiKey": GEOAPIFY_API_KEY,
        "limit": 1,
    }

    response = requests.get(url, params=params)

    response.raise_for_status()

    data = response.json()

    if len(data["features"]) == 0:
        raise Exception("Location not found")

    coords = data["features"][0]["geometry"]["coordinates"]

    return {
        "lon": coords[0],
        "lat": coords[1],
    }


if __name__ == "__main__":

    print(geocode("Spiti Valley"))
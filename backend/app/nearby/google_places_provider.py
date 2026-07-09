import requests
from app.config import GOOGLE_PLACES_API_KEY
from app.nearby.nearby_categories import NEARBY_CATEGORIES

SEARCH_NEARBY_URL = "https://places.googleapis.com/v1/places:searchNearby"

FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.location",
    "places.rating",
    "places.userRatingCount",
    "places.types",
    "places.primaryType"
])

def search_nearby_for_category(
        lat: float,
        lon: float,
        category: str,
        radius_m: int,
        max_results: int,
) -> list[dict]:
    #One searchNearby call restricted to the Googel types belonging to a single one of our categories (culture/nature/food/shopping)
    included_types = NEARBY_CATEGORIES[category]
    print("INCLUDED TYPES:",included_types)

    body = {
        "includedTypes": included_types,
        "maxResultCount": max_results,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lon},
                "radius": radius_m
            }
        },
        "rankPreference": "POPULARITY"
    }
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": FIELD_MASK
    }

    try:
        response = requests.post(SEARCH_NEARBY_URL, json=body,headers=headers,timeout=30)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException,ValueError) as e:
        print(f"[google_places] searchNearby failed for category={category} at ({lat},{lon}): {e}")
        return []
    
    return data.get("places",[])

def fetch_sights_for_destination(
        lat: float,
        lon: float,
        radius_m: int = 20000,
        max_results_per_category: int = 15,
) -> list[dict]:
    #Fetched candidate sights across ALL four categories for a destination
    #Returns a list of NORMALIZED dicts
    all_places = []
    for category in NEARBY_CATEGORIES: 
        places = search_nearby_for_category(
            lat=lat,
            lon=lon,
            category=category,
            radius_m=radius_m,
            max_results=max_results_per_category
        )
        for place in places: 
            place["our_category"] = category
        all_places.extend(places)
    return normalize_places(all_places)

def normalize_places(raw_places: list[dict]) -> list[dict]:
    #Converts Google's raw place objects into RawSight expects

    normalized = []

    for place in raw_places:
        location = place.get("location", {})
        display_name = place.get("displayName", {})
        normalized.append({
            "place_id": place.get("id",""),
            "name": display_name.get("text", "Unnamed"),
            "lat": location.get("latitude"),
            "lon": location.get("longitude"),
            "rating": place.get("rating"),
            "review_count": place.get("userRatingCount"),
            "category": place.get("our_category", "culture"),
            "raw_types": place.get("types", []),
        })
    return normalized
    
if __name__ == "__main__":
    sights = fetch_sights_for_destination(lat=28.6139,lon=77.2090)
    print(f"Found {len(sights)} sights\n")
    for s in sights[:10]:
        print(f"[{s['category']}] {s['name']} — rating {s['rating']} ({s['review_count']} reviews)")
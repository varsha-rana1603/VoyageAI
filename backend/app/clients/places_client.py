"""
Google Places API (new v1 API, not the legacy one) client.

Uses header-based auth: X-Goog-Api-Key and X-Goog-FieldMask. The field mask
is built once as FIELD_MASK below and reused everywhere -- this is
deliberate. A past integration bug came from a typo'd header
(X-Goog_FieldMask, underscore instead of hyphen) causing silent 400s; having
one shared constant means there's exactly one place that spelling can go
wrong, not one per call site.
"""
import httpx

from app.config import settings

PLACES_BASE_URL = "https://places.googleapis.com/v1/places"

# Only request what's actually used downstream -- Places bills partly by
# field count, and unused fields are just extra failure surface.
FIELD_MASK = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.location",
        "places.types",
        "places.editorialSummary",
        "places.priceLevel",
        "places.userRatingCount",
        "places.rating",
    ]
)

ATTRACTION_FIELD_MASK = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.location",
        "places.types",
        "places.rating",
        "places.userRatingCount",
        "places.editorialSummary",
        "places.regularOpeningHours",
        "places.websiteUri",
        "places.photos",
    ]
)

DETAILS_FIELD_MASK = ",".join(
    [
        "id",
        "displayName",
        "formattedAddress",
        "addressComponents",
        "location",
        "types",
        "editorialSummary",
        "priceLevel",
        "userRatingCount",
        "rating",
    ]
)

VALID_DESTINATION_TYPES = {
    "locality",
    "administrative_area_level_1",
    "country"
}


def validate_destination(place):

    types = set(place.get("types", []))

    if not types.intersection(
        VALID_DESTINATION_TYPES
    ):
        raise PlacesLookupError(
            "Not a valid destination"
        )


class PlacesLookupError(Exception):
    """Raised when a destination can't be resolved -- caller should fail
    loudly on this rather than insert a partial/blank row."""


def _headers(field_mask: str) -> dict:
    if not settings.google_places_api_key:
        raise PlacesLookupError("GOOGLE_PLACES_API_KEY is not set in .env")
    return {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.google_places_api_key,
        "X-Goog-FieldMask": field_mask,
    }


def search_destination(query: str) -> dict:
    """
    Text Search for a destination by name (e.g. "Udaipur, India"). Returns
    the raw top result dict from Places, or raises PlacesLookupError if
    nothing is found -- no silent empty-result fallback.
    """
    response = httpx.post(
        f"{PLACES_BASE_URL}:searchText",
        headers=_headers(FIELD_MASK),
        json={"textQuery": query, "maxResultCount": 1},
        timeout=15.0,
    )
    if response.status_code != 200:
        raise PlacesLookupError(f"Places search failed for '{query}': {response.status_code} {response.text}")

    results = response.json().get("places", [])
    if not results:
        raise PlacesLookupError(f"No Places result found for '{query}'")
    return results[0]


def get_place_details(place_id: str) -> dict:
    """Fetch fuller details for a place_id -- used when Text Search's summary
    fields aren't enough (e.g. addressComponents for a reliable country)."""
    response = httpx.get(
        f"{PLACES_BASE_URL}/{place_id}",
        headers=_headers(DETAILS_FIELD_MASK),
        timeout=15.0,
    )

    print("RESPONSE: ", response)
    if response.status_code != 200:
        raise PlacesLookupError(f"Place details failed for '{place_id}': {response.status_code} {response.text}")
    return normalize_place(
    response.json()
)


def extract_country(place: dict) -> str:
    """
    Pull country from addressComponents if present (most reliable), falling
    back to parsing the last comma-segment of formattedAddress. Raises rather
    than returning an empty string -- country is a required model field.
    """
    for component in place.get("addressComponents", []):
        if "country" in component.get("types", []):
            return component.get("longText") or component.get("shortText")

    formatted = place.get("formattedAddress", "")
    if formatted:
        return formatted.split(",")[-1].strip()

    raise PlacesLookupError(f"Could not determine country for place {place.get('id')}")

def normalize_place(place: dict) -> dict:

    return {
        "google_place_id": place["id"],

        "name": place["displayName"]["text"],

        "country": extract_country(place),

        "latitude": place["location"]["latitude"],

        "longitude": place["location"]["longitude"],

        "types": place.get("types", []),

        "rating": place.get("rating"),

        "rating_count": place.get("userRatingCount", 0),

        "description": (
            place.get("editorialSummary", {})
            .get("text")
        ),
    }

HOTEL_FIELD_MASK = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.location",
        "places.types",
        "places.rating",
        "places.userRatingCount",
        "places.priceLevel",
        "places.websiteUri",
        "places.photos",
    ]
)


def search_destination_accommodations(
    query: str,
    limit: int = 20,
) -> list[dict]:    
    response = httpx.post(
        f"{PLACES_BASE_URL}:searchText",
        headers=_headers(HOTEL_FIELD_MASK),
        json={
            "textQuery": query,
            "maxResultCount": limit,
        },
        timeout=20.0,
    )

    # print("RESPONSE: ", response.json().get("places"))

    if response.status_code != 200:
        raise PlacesLookupError(
            f"Accommodation search failed for '{query}': "
            f"{response.status_code} {response.text}"
        )

    return response.json().get("places", [])

def search_destination_attractions(
    query: str,
    latitude: float,
    longitude: float,
    radius_meters: int = 20_000,
    limit: int = 20,
) -> list[dict]:
    """
    Search Google Places for attractions within a circular radius.

    Example:
        query="bookstores"
        latitude=41.9028
        longitude=12.4964
        radius_meters=20000
    """

    response = httpx.post(
        f"{PLACES_BASE_URL}:searchText",
        headers=_headers(ATTRACTION_FIELD_MASK),
        json={
            "textQuery": query,
            "maxResultCount": limit,
            "locationBias": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                    "radius": radius_meters,
                }
            },
        },
        timeout=20.0,
    )

    if response.status_code != 200:
        raise PlacesLookupError(
            f"Attraction search failed for '{query}': "
            f"{response.status_code} {response.text}"
        )

    return response.json().get("places", [])
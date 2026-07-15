# """
# Amadeus self-service API client.

# Getting an average nightly hotel rate for a destination is a 3-step chain:
#   1. OAuth2 client-credentials token (self-service APIs are pay-as-you-go
#      with a free monthly quota, not a static API key)
#   2. Resolve destination name -> IATA city code (Amadeus indexes hotels by
#      city code, not free-text name)
#   3. List hotels in that city, then fetch live offers for a sample of them
#      and average the nightly price

# Each step can fail independently (city not found, no hotels listed, no
# offers available for those hotels), and each failure should be explicit --
# the loader needs to know which destinations it couldn't get real pricing
# for, rather than silently defaulting to a guessed number.

# Destination
#       |
#       ↓
# Find hotels
#       |
#       ↓
# Get average nightly price
#       |
#       ↓
# Convert to INR
#       |
#       ↓
# avg_daily_cost_inr
# """
# import time

# import httpx

# from app.config import settings

# TOKEN_URL = f"{settings.amadeus_base_url}/v1/security/oauth2/token"
# CITY_SEARCH_URL = f"{settings.amadeus_base_url}/v1/reference-data/locations"
# HOTEL_LIST_URL = f"{settings.amadeus_base_url}/v1/reference-data/locations/hotels/by-city"
# HOTEL_OFFERS_URL = f"{settings.amadeus_base_url}/v3/shopping/hotel-offers"

# # Module-level token cache -- avoids re-authenticating on every destination
# # in a loader run that processes dozens of destinations in one pass.
# _token_cache = {"access_token": None, "expires_at": 0}


# class AmadeusLookupError(Exception):
#     pass


# def _get_access_token() -> str:
#     if _token_cache["access_token"] and time.time() < _token_cache["expires_at"] - 30:
#         return _token_cache["access_token"]

#     if not settings.amadeus_api_key or not settings.amadeus_api_secret:
#         raise AmadeusLookupError("AMADEUS_API_KEY / AMADEUS_API_SECRET not set in .env")

#     response = httpx.post(
#         TOKEN_URL,
#         data={
#             "grant_type": "client_credentials",
#             "client_id": settings.amadeus_api_key,
#             "client_secret": settings.amadeus_api_secret,
#         },
#         timeout=15.0,
#     )
#     if response.status_code != 200:
#         raise AmadeusLookupError(f"Amadeus auth failed: {response.status_code} {response.text}")

#     data = response.json()
#     _token_cache["access_token"] = data["access_token"]
#     _token_cache["expires_at"] = time.time() + data.get("expires_in", 1800)
#     return _token_cache["access_token"]


# def _auth_headers() -> dict:
#     return {"Authorization": f"Bearer {_get_access_token()}"}


# def resolve_city_code(city_name: str) -> str:
#     response = httpx.get(
#         CITY_SEARCH_URL,
#         headers=_auth_headers(),
#         params={"keyword": city_name, "subType": "CITY"},
#         timeout=15.0,
#     )
#     if response.status_code != 200:
#         raise AmadeusLookupError(f"City search failed for '{city_name}': {response.status_code} {response.text}")

#     results = response.json().get("data", [])
#     if not results:
#         raise AmadeusLookupError(f"No Amadeus city code found for '{city_name}'")
#     return results[0]["iataCode"]


# def _get_hotel_ids(city_code: str, limit: int = 10) -> list[str]:
#     response = httpx.get(
#         HOTEL_LIST_URL,
#         headers=_auth_headers(),
#         params={"cityCode": city_code},
#         timeout=15.0,
#     )
#     if response.status_code != 200:
#         raise AmadeusLookupError(f"Hotel list failed for city '{city_code}': {response.status_code} {response.text}")

#     hotels = response.json().get("data", [])
#     if not hotels:
#         raise AmadeusLookupError(f"No hotels listed for city '{city_code}'")
#     return [h["hotelId"] for h in hotels[:limit]]


# def average_nightly_rate_inr(city_name: str) -> float:
#     """
#     Returns the average nightly hotel rate across a sample of hotels in the
#     given city, in INR. Raises AmadeusLookupError on any failure in the
#     chain -- callers (the loader) should treat this as "no real pricing
#     available for this destination" and either skip the row or fall back
#     to a clearly-flagged estimate, not silently insert a wrong number.
#     """
#     city_code = resolve_city_code(city_name)
#     hotel_ids = _get_hotel_ids(city_code)

#     response = httpx.get(
#         HOTEL_OFFERS_URL,
#         headers=_auth_headers(),
#         params={
#             "hotelIds": ",".join(hotel_ids),
#             "adults": 1,
#             "currency": "INR",
#             "bestRateOnly": "true",
#         },
#         timeout=20.0,
#     )
#     if response.status_code != 200:
#         raise AmadeusLookupError(f"Hotel offers failed for '{city_name}': {response.status_code} {response.text}")

#     offers_data = response.json().get("data", [])
#     nightly_rates = []
#     for hotel_offer in offers_data:
#         for offer in hotel_offer.get("offers", []):
#             price = offer.get("price", {})
#             total = price.get("total")
#             nights = offer.get("roomInformation", {}).get("nights") or 1
#             if total is not None:
#                 nightly_rates.append(float(total) / max(nights, 1))

#     if not nightly_rates:
#         raise AmadeusLookupError(f"No priced offers available for hotels in '{city_name}'")

#     return round(sum(nightly_rates) / len(nightly_rates), 2)
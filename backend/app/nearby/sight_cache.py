
import time

from app.nearby.google_places_provider import fetch_sights_for_destination

_CACHE_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days — sight data (landmarks, ratings) drifts slowly

# { destination_key: (timestamp, sights_list) }
_sight_cache: dict = {}


def _cache_key(destination_name: str) -> str:
    return destination_name.strip().lower()


def get_sights_for_destination(
    destination_name: str,
    lat: float,
    lon: float,
    force_refresh: bool = False,
) -> list[dict]:
    key = _cache_key(destination_name)

    if not force_refresh:
        cached = _sight_cache.get(key)
        if cached and (time.time() - cached[0]) < _CACHE_TTL_SECONDS:
            return cached[1]

    sights = fetch_sights_for_destination(lat=lat, lon=lon)
    _sight_cache[key] = (time.time(), sights)
    return sights


def invalidate(destination_name: str) -> None:
    _sight_cache.pop(_cache_key(destination_name), None)


def cache_stats() -> dict:
    now = time.time()
    return {
        key: {
            "sight_count": len(sights),
            "age_seconds": round(now - timestamp, 1),
        }
        for key, (timestamp, sights) in _sight_cache.items()
    }


if __name__ == "__main__":
    sights_1 = get_sights_for_destination("Delhi", lat=28.6139, lon=77.2090)
    print(f"First call: {len(sights_1)} sights (cache miss, fetched fresh)\n")
    sights_2 = get_sights_for_destination("Delhi", lat=28.6139, lon=77.2090)
    print(f"Second call: {len(sights_2)} sights (should be cache hit, no fetch logs above this line)\n")

    print("Cache stats:", cache_stats())
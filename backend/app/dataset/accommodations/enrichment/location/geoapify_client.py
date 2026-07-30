from collections.abc import Sequence

import requests

from app.config import settings


class GeoapifyClient:

    BASE_URL = (
        "https://api.geoapify.com/v2/places"
    )

    def nearby_places(
        self,
        *,
        latitude: float,
        longitude: float,
        radius: int,
        categories: Sequence[str],
        limit: int = 500,
    ) -> list[dict]:

        params = {
            "categories": ",".join(categories),
            "filter": (
                f"circle:{longitude},"
                f"{latitude},"
                f"{radius}"
            ),
            "bias": (
                f"proximity:{longitude},"
                f"{latitude}"
            ),
            "limit": limit,
            "apiKey": settings.geoapify_api_key,
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=30,
        )

        if response.status_code != 200:
            print(response.text)

        response.raise_for_status()

        data = response.json()

        return data.get(
            "features",
            [],
        )
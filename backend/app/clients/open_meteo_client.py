from datetime import date
import httpx

from app.config import settings


class ClimateLookupError(Exception):
    pass



def fetch_daily_climate(
    latitude: float,
    longitude: float
) -> dict:

    today = date.today()

    end_date = date(
        today.year - 1,
        12,
        31
    )

    start_date = date(
        today.year - 3,
        1,
        1
    )


    response = httpx.get(
        settings.open_meteo_base_url,
        params={
            "latitude": latitude,
            "longitude": longitude,

            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),

            "daily":
                "temperature_2m_mean,precipitation_sum",

            "timezone": "auto"
        },

        timeout=20
    )


    if response.status_code != 200:
        raise ClimateLookupError(
            response.text
        )


    data = response.json().get(
        "daily"
    )


    if not data:
        raise ClimateLookupError(
            "No climate data returned"
        )


    return data
from app.clients.open_meteo_client import (
    fetch_daily_climate
)


MONTH_NAMES = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec"
]


IDEAL_TEMP_RANGE_C = (
    18,
    28
)


MAX_TEMP_DELTA = 15



def comfort_score(
    avg_temp,
    rainfall
):

    low, high = IDEAL_TEMP_RANGE_C


    if low <= avg_temp <= high:

        temp_score = 1

    else:

        delta = (
            low - avg_temp
            if avg_temp < low
            else avg_temp - high
        )

        temp_score = max(
            0,
            1 - delta / MAX_TEMP_DELTA
        )


    rain_score = max(
        0,
        1 - rainfall / 200
    )


    return round(
        0.6 * temp_score +
        0.4 * rain_score,
        4
    )



def monthly_comfort_scores(
    latitude,
    longitude
):

    daily = fetch_daily_climate(
        latitude,
        longitude
    )


    temperatures = {
        m: []
        for m in range(1,13)
    }

    rainfall = {
        m: []
        for m in range(1,13)
    }


    for (
        date,
        temp,
        rain
    ) in zip(
        daily["time"],
        daily["temperature_2m_mean"],
        daily["precipitation_sum"]
    ):

        month = int(
            date.split("-")[1]
        )


        if temp:
            temperatures[month].append(temp)


        if rain:
            rainfall[month].append(rain)



    scores = {}


    for month in range(1,13):

        temps = temperatures[month]
        rains = rainfall[month]


        if not temps:

            scores[month] = 0.5
            continue


        avg_temp = (
            sum(temps) / len(temps)
            if temps else 20
        )

        avg_rain = (
            (sum(rains) / len(rains)) * 30
            if rains else 0
        )

        scores[month] = comfort_score(
            avg_temp,
            avg_rain
        )


    return scores



def get_climate_profile(
    latitude,
    longitude
):

    scores = monthly_comfort_scores(
        latitude,
        longitude
    )


    ranked = sorted(
        scores.items(),
        key=lambda x:x[1],
        reverse=True
    )


    best = sorted(
        [
            m
            for m,_ in ranked[:3]
        ]
    )


    worst = sorted(
        [
            m
            for m,_ in ranked[-3:]
        ]
    )


    return {
        "best_season":
            format_months(best),

        "worst_season":
            format_months(worst),

        "monthly_scores":
            scores
    }



def format_months(months):

    if not months:
        return "year-round"


    months = sorted(months)


    names = [
        MONTH_NAMES[m-1]
        for m in months
    ]


    # normal contiguous range
    if all(
        months[i] == months[i-1] + 1
        for i in range(1, len(months))
    ):
        return f"{names[0]}-{names[-1]}"


    # handle year wrapping:
    # Nov, Dec, Jan
    if set(months) == {11,12,1}:
        return "Nov-Jan"


    return ",".join(names)
from app.nearby.nearby_service import get_nearby_places
from app.nearby.preference_engine import compute_category_weights


stays = [

    {
        "name":"Taj Palace",
        "lat":28.5988,
        "lon":77.1734
    }

]


weights = compute_category_weights(
    travel_style="Cultural",
    budget="medium",
    crowd_tolerance="medium",
    terrain="city",
    free_text="I want to explore history and architecture"
)


result = get_nearby_places(

    destination_lat=28.6139,

    destination_lon=77.2090,

    category_weights=weights,

    recommended_stays=stays

)


for sight in result["sights"][:5]:

    print("\n", sight["name"])

    print(
        sight["why"]
    )

    print(
        "Nearby stays:",
        sight["nearby_stays"]
    )


print("\nSTAYS\n")

for stay in result["stays"]:

    print(
        stay["name"]
    )

    print(
        stay["nearby_sights"]
    )
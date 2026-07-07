from pprint import pprint

from app.stay.recommender import get_stay_recommendations

recommendations = get_stay_recommendations(
    destination_name="Spiti Valley",
    travel_style="Adventure",
    budget="Medium",
    crowd_tolerance="Avoid",
    terrain="Mountains",
    free_text="I want a quiet place with mountain views, nearby cafes and good food."
)

print("\n==========================================")
print(f"Found {len(recommendations)} recommendations")
print("==========================================\n")

for i, stay in enumerate(recommendations, start=1):

    print("=" * 70)
    print(f"{i}. {stay['name']}")
    print("=" * 70)

    pprint(stay)

    print()
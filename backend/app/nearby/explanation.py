#Generates personalised 'Why' text for each ranked sight

import hashlib

CATEGORY_INTROS = {
    "culture": {
        "strong": [
            "Since you enjoy history and cultural experiences,",
            "Because you're drawn to heritage and architecture,",
            "As someone who loves exploring the past,",
        ],
        "moderate": [
            "You mentioned some interest in culture, so",
            "Since culture is part of what you're looking for,",
        ],
        "soft": [
            "Even though it's not your main focus,",
            "As a change of pace from your usual interests,",
        ],
    },
    "nature": {
        "strong": [
            "Since you prefer peaceful, natural surroundings,",
            "Because you enjoy the outdoors,",
            "As someone who loves nature,",
        ],
        "moderate": [
            "You mentioned enjoying nature, so",
            "Since some outdoor time appeals to you,",
        ],
        "soft": [
            "Even though it's not your main focus,",
            "For a quick breath of fresh air,",
        ],
    },
    "food": {
        "strong": [
            "Since you enjoy discovering local cuisine,",
            "Because good food is a priority for your trip,",
            "As a food lover,",
        ],
        "moderate": [
            "You mentioned caring about food, so",
            "Since local flavors matter to you,",
        ],
        "soft": [
            "Even though dining out isn't your main focus,",
            "For a quick bite nearby,",
        ],
    },
    "shopping": {
        "strong": [
            "Since you enjoy browsing local markets,",
            "Because shopping is part of how you like to travel,",
            "As someone who enjoys picking up local finds,",
        ],
        "moderate": [
            "You mentioned some interest in shopping, so",
            "Since browsing local stores appeals to you,",
        ],
        "soft": [
            "Even though it's not your main focus,",
            "If you have a spare hour,",
        ],
    },
}


def _tone_tier(category: str, category_weights: dict) -> str:
    ranked_categories = sorted(category_weights.items(), key=lambda kv: -kv[1])
    position = next(
        (i for i, (cat, _) in enumerate(ranked_categories) if cat == category),
        len(ranked_categories) - 1,
    )

    if position == 0:
        return "strong"
    if position == 1:
        return "moderate"
    return "soft"


def _quality_clause(sight: dict) -> str:
    review_count = sight.get("review_count") or 0
    popularity_score = sight.get("popularity_score", 50)

    if review_count >= 10000:
        return f"{sight['name']} is a well-loved favorite, visited by thousands of travelers"
    if popularity_score >= 85:
        return f"{sight['name']} is highly rated by visitors"
    if popularity_score >= 65:
        return f"{sight['name']} is a solid, well-regarded choice"
    return f"{sight['name']} is worth exploring"


def _distance_clause(sight: dict) -> str:
    distance_km = sight.get("distance_km", 0)

    if distance_km <= 3:
        return "right in the heart of the destination"
    if distance_km <= 8:
        return "just a short trip from the center"
    return "a bit further out, but worth the detour"


def generate_sight_explanation(sight: dict, category_weights: dict) -> str:
    category = sight.get("category", "culture")
    tier = _tone_tier(category, category_weights)

    intro_options = CATEGORY_INTROS.get(category, CATEGORY_INTROS["culture"])[tier]

    # Deterministic "random" pick — stable across repeated calls for the
    # same place, but varied ACROSS different places so 10 culture sights
    # in a row don't all open with the identical sentence.
    place_id = sight.get("place_id", sight.get("name", ""))
    pick_index = int(hashlib.md5(place_id.encode()).hexdigest(), 16) % len(intro_options)
    intro = intro_options[pick_index]

    quality = _quality_clause(sight)
    distance = _distance_clause(sight)

    return f"{intro} {quality}, {distance}."


def explain_sights(ranked_sights: list, category_weights: dict) -> list:
    return [
        {**sight, "why": generate_sight_explanation(sight, category_weights)}
        for sight in ranked_sights
    ]


if __name__ == "__main__":
    from app.nearby.sight_cache import get_sights_for_destination
    from app.nearby.preference_engine import compute_category_weights
    from app.nearby.ranking import rank_sights

    dest_lat, dest_lon = 28.6139, 77.2090  # Delhi

    sights = get_sights_for_destination("Delhi", lat=dest_lat, lon=dest_lon)

    weights = compute_category_weights(
        travel_style="Cultural",
        budget="medium",
        crowd_tolerance="medium",
        terrain="city",
        free_text="I want to explore history and architecture",
    )

    ranked = rank_sights(sights, weights, dest_lat, dest_lon)
    explained = explain_sights(ranked, weights)

    print("Top 5 with explanations:\n")
    for s in explained[:5]:
        print(f"{s['name']} ({s['category']}, score={s['final_score']})")
        print(f"  \"{s['why']}\"\n")

    # Also show a LOW-weighted category's explanation, to confirm the
    # "soft" tone kicks in correctly for something the user barely mentioned
    shopping_sights = [s for s in explained if s["category"] == "shopping"]
    if shopping_sights:
        print("A shopping sight (should use SOFT tone, since culture dominates):\n")
        print(f"{shopping_sights[0]['name']}")
        print(f"  \"{shopping_sights[0]['why']}\"")
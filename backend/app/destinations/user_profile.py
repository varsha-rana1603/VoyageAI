def normalize_travel_style(style: str) -> str:
    style = style.strip().lower()

    aliases = {
        "adventure": "adventure",
        "adventures": "adventure",

        "relax": "relax",
        "relaxed": "relax",
        "relaxation": "relax",
        "peaceful": "relax",

        "culture": "cultural",
        "cultural": "cultural",
        "history": "cultural",
        "historical": "cultural",
        "heritage": "cultural",

        "luxury": "luxury",
        "premium": "luxury",

        "offbeat": "offbeat",
        "off-beat": "offbeat",
        "hidden": "offbeat",
        "hidden gems": "offbeat",
        "unique": "offbeat",
    }

    return aliases.get(style, "adventure")


def normalize_budget(budget):
    budget = str(budget).strip().lower()

    aliases = {
        "cheap": "low",
        "low": "low",
        "budget": "low",

        "medium": "medium",
        "mid": "medium",
        "moderate": "medium",

        "high": "luxury",
        "luxury": "luxury",
        "premium": "luxury",
        "expensive": "luxury",
    }

    return aliases.get(budget, "medium")


def normalize_crowd(crowd):
    crowd = crowd.strip().lower()

    aliases = {
        "avoid": "low",
        "avoid crowds": "low",
        "low": "low",
        "quiet": "low",
        "peaceful": "low",

        "medium": "medium",
        "some": "medium",
        "some crowds": "medium",
        "some_ok": "medium",

        "high": "high",
        "love crowds": "high",
        "busy": "high",
        "crowded": "high",
        "love_crowds": "high",
    }

    return aliases.get(crowd, "medium")


def normalize_terrain(terrain):
    terrain = terrain.strip().lower()

    aliases = {
        "mountain": "mountains",
        "mountains": "mountains",
        "hill": "mountains",
        "hills": "mountains",

        "beach": "beach",
        "beaches": "beach",
        "coast": "beach",

        "city": "city",
        "urban": "city",

        "forest": "forest",
        "forests": "forest",
        "jungle": "forest",

        "desert": "desert",
        "deserts": "desert",

        "backwater": "backwaters",
        "backwaters": "backwaters",
    }

    return aliases.get(terrain, "city")


def build_user_profile(
    travel_style,
    budget,
    crowd_tolerance,
    terrain,
    free_text=""
):
    """
    Converts quiz answers into:
    1. Numeric profile
    2. Semantic text description
    """

    travel_style = normalize_travel_style(travel_style)
    budget = normalize_budget(budget)
    crowd_level = normalize_crowd(crowd_tolerance)
    terrain = normalize_terrain(terrain)

    style_map = {
        "adventure": {
            "adventure_score": 9,
            "nature_score": 8,
            "luxury_score": 2,
            "nightlife_score": 2,
            "culture_score": 4,
            "food_scene_score": 5,
            "family_friendly_score": 4,
        },

        "relax": {
            "adventure_score": 2,
            "nature_score": 7,
            "luxury_score": 6,
            "nightlife_score": 2,
            "culture_score": 4,
            "food_scene_score": 6,
            "family_friendly_score": 7,
        },

        "cultural": {
            "adventure_score": 3,
            "nature_score": 4,
            "luxury_score": 4,
            "nightlife_score": 2,
            "culture_score": 9,
            "food_scene_score": 7,
            "family_friendly_score": 6,
        },

        "luxury": {
            "adventure_score": 3,
            "nature_score": 5,
            "luxury_score": 9,
            "nightlife_score": 5,
            "culture_score": 5,
            "food_scene_score": 8,
            "family_friendly_score": 6,
        },

        "offbeat": {
            "adventure_score": 7,
            "nature_score": 9,
            "luxury_score": 2,
            "nightlife_score": 1,
            "culture_score": 6,
            "food_scene_score": 4,
            "family_friendly_score": 3,
        },
    }

    numeric_profile = style_map[travel_style].copy()

    numeric_profile["budget_level"] = budget
    numeric_profile["desired_crowd_level"] = crowd_level
    numeric_profile["terrain"] = terrain

    text_description = (
        f"A traveler looking for a {travel_style} experience, "
        f"preferring {terrain}, "
        f"with a {budget} budget, "
        f"and prefers {crowd_level} crowds. "
    )

    if free_text:
        text_description += free_text

    return numeric_profile, text_description


if __name__ == "__main__":
    profile, text = build_user_profile(
        travel_style="Culture",
        budget="Premium",
        crowd_tolerance="Avoid Crowds",
        terrain="Mountain",
        free_text="Shopping streets and cozy cafés."
    )

    print(profile)
    print(text)
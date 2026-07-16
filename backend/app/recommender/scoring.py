#weighted scoring

from app.conversation.user_profile import UserProfile
from app.models.destination import Destination
from app.recommender.candidate_search import CandidateDestination
from dataclasses import dataclass

@dataclass
class ScoreResult:
    score: float
    matched_features: list[str]

def metadata(
    destination: Destination,
) -> dict:

    return destination.cost_profile.get(
        "metadata",
        {},
    )

def metadata_score(
    destination: Destination,
    key: str,
) -> float:

    return (
        metadata(destination)
        .get(key, 0)
    ) / 10

def semantic_score(candidate: CandidateDestination) -> float:
    #Returns semantic similarity from embedding search
    return candidate.semantic_score

def terrain_score(profile: UserProfile, destination: Destination) -> float:
    if not profile.terrain_preferences:
        return 0.5
    overlap = set(profile.terrain_preferences).intersection(destination.terrain)
    return len(overlap) / len(profile.terrain_preferences)

def travel_style_score(profile: UserProfile,destination: Destination) -> float:
    if not profile.travel_styles:
        return 0.5
    overlap = set(profile.travel_styles).intersection(destination.travel_styles)
    return len(overlap) / len(profile.travel_styles)

def crowd_score(
    profile: UserProfile,
    destination: Destination,
) -> float:

    if profile.crowd_preference is None:
        return 0.5

    if (
        profile.crowd_preference
        == destination.typical_crowd_level
    ):
        return 1.0

    return 0.0

def get_daily_budget(profile: UserProfile) -> float | None:

    if profile.duration_days is None:
        return None

    if profile.total_budget is not None:
        return profile.total_budget / profile.duration_days

    if profile.maximum_budget is not None:
        return profile.maximum_budget / profile.duration_days

    if profile.minimum_budget is not None:
        return profile.minimum_budget / profile.duration_days

    return None

def budget_score(
    profile: UserProfile,
    destination: Destination,
) -> float:
    #VoyageAI should intelligently pick the closest accommodation tier based on the user's daily budget

    daily_budget = get_daily_budget(profile)

    if daily_budget is None:
        return 0.5

    daily = destination.cost_profile.get(
        "daily_cost",
        {},
    )

    totals = []

    for tier in [
        "budget",
        "mid_range",
        "luxury",
    ]:

        if tier not in daily:
            continue

        cost = sum(
            daily[tier].values()
        )

        totals.append(cost)

    if not totals:
        return 0.5

    closest = min(
        totals,
        key=lambda x: abs(
            x - daily_budget
        )
    )

    ratio = min(
        daily_budget,
        closest,
    ) / max(
        daily_budget,
        closest,
    )

    return ratio

def lifestyle_score(
    profile: UserProfile,
    destination: Destination,
) -> float:

    scores = []

    if profile.food_importance is not None:

        scores.append(
            profile.food_importance / 10
            * metadata_score(
                destination,
                "food_score",
            )
        )

    if profile.culture_importance is not None:

        scores.append(
            profile.culture_importance / 10
            * metadata_score(
                destination,
                "culture_score",
            )
        )

    if profile.relaxation_importance is not None:

        scores.append(
            profile.relaxation_importance / 10
            * metadata_score(
                destination,
                "relaxation_score",
            )
        )

    if profile.adventure_importance is not None:

        scores.append(
            profile.adventure_importance / 10
            * metadata_score(
                destination,
                "adventure_score",
            )
        )

    if profile.nature_importance is not None:

        scores.append(
            profile.nature_importance / 10
            * metadata_score(
                destination,
                "nature_score",
            )
        )

    if profile.nightlife_importance is not None:

        nightlife = metadata(destination).get(
            "nightlife",
            "medium",
        )

        mapping = {
            "low": 0.3,
            "medium": 0.7,
            "high": 1.0,
        }

        scores.append(
            profile.nightlife_importance / 10
            * mapping.get(
                nightlife,
                0.7,
            )
        )

    if not scores:
        return 0.5

    return sum(scores) / len(scores)

def calculate_final_score(
    profile: UserProfile,
    candidate: CandidateDestination,
) -> float:

    destination = candidate.destination

    score = (
        semantic_score(candidate) * 0.35
        + terrain_score(profile, destination) * 0.15
        + travel_style_score(profile, destination) * 0.15
        + budget_score(profile, destination) * 0.15
        + crowd_score(profile, destination) * 0.10
        + lifestyle_score(profile, destination) * 0.10
    )

    return round(score, 4)


#Recommend destinations that are good when the user actually wants to tarvel
MONTHS = [
    "jan", "feb", "mar", "apr",
    "may", "jun", "jul", "aug",
    "sep", "oct", "nov", "dec",
]


def expand_month_range(
    season: str | None,
) -> set[str]:

    if not season:
        return set()

    season = season.strip().lower()

    # Handle "All year"
    if season in {"all year", "year-round", "year round"}:
        return set(MONTHS)

    # Handle a single month like "October"
    if "-" not in season:
        month = season[:3]
        if month in MONTHS:
            return {month}
        return set()

    start, end = season.split("-", 1)

    start = start.strip()[:3]
    end = end.strip()[:3]

    if start not in MONTHS or end not in MONTHS:
        return set()

    start_idx = MONTHS.index(start)
    end_idx = MONTHS.index(end)

    if start_idx <= end_idx:
        return set(MONTHS[start_idx:end_idx + 1])

    return set(
        MONTHS[start_idx:] +
        MONTHS[:end_idx + 1]
    )

def season_score(
    profile: UserProfile,
    destination: Destination,
) -> float:

    if profile.travel_month is None:
        return 0.5

    month = profile.travel_month[:3].lower()

    best = expand_month_range(
        destination.best_season
    )

    worst = expand_month_range(
        destination.worst_season
    )

    if month in best:
        return 1.0

    if month in worst:
        return 0.0

    return 0.5

def calculate_final_score(
    profile: UserProfile,
    candidate: CandidateDestination,
) -> float:

    destination = candidate.destination

    weights = {

        "semantic": 0.30,

        "budget": 0.20,

        "terrain": 0.10,

        "travel_style": 0.10,

        "season": 0.10,

        "lifestyle": 0.10,

        "crowd": 0.10,
    }

    score = (

        semantic_score(candidate)
        * weights["semantic"]

        + budget_score(
            profile,
            destination,
        )
        * weights["budget"]

        + terrain_score(
            profile,
            destination,
        )
        * weights["terrain"]

        + travel_style_score(
            profile,
            destination,
        )
        * weights["travel_style"]

        + season_score(
            profile,
            destination,
        )
        * weights["season"]

        + lifestyle_score(
            profile,
            destination,
        )
        * weights["lifestyle"]

        + crowd_score(
            profile,
            destination,
        )
        * weights["crowd"]

    )

    return round(score, 4)

def build_matched_features(
    profile: UserProfile,
    candidate: CandidateDestination,
) -> list[str]:

    destination = candidate.destination

    matches = []

    # Semantic similarity
    if candidate.semantic_score >= 0.80:
        matches.append("strong semantic match to the user's travel preferences")
    elif candidate.semantic_score >= 0.65:
        matches.append("good overall match to the user's travel preferences")

    # Terrain
    terrain_overlap = (
        set(profile.terrain_preferences)
        & set(destination.terrain)
    )

    if terrain_overlap:
        matches.append(
            f"preferred terrain: {', '.join(sorted(terrain_overlap))}"
        )

    # Travel styles
    style_overlap = (
        set(profile.travel_styles)
        & set(destination.travel_styles)
    )

    if style_overlap:
        matches.append(
            f"travel style: {', '.join(sorted(style_overlap))}"
        )

    # Budget
    if budget_score(profile, destination) >= 0.75:
        matches.append(
            "fits the user's budget"
        )

    # Season
    if season_score(profile, destination) == 1.0:
        matches.append(
            f"excellent during {profile.travel_month}"
        )

    # Crowd preference
    if (
        profile.crowd_preference
        and profile.crowd_preference
        == destination.typical_crowd_level
    ):
        matches.append(
            f"{profile.crowd_preference} crowd levels"
        )

    metadata = destination.cost_profile.get(
        "metadata",
        {},
    )

    # Food
    if (
        profile.food_importance
        and profile.food_importance >= 7
        and metadata.get("food_score", 0) >= 7
    ):
        matches.append(
            "excellent food scene"
        )

    # Adventure
    if (
        profile.adventure_importance
        and profile.adventure_importance >= 7
        and metadata.get("adventure_score", 0) >= 7
    ):
        matches.append(
            "great adventure opportunities"
        )

    # Relaxation
    if (
        profile.relaxation_importance
        and profile.relaxation_importance >= 7
        and metadata.get("relaxation_score", 0) >= 7
    ):
        matches.append(
            "ideal for relaxation"
        )

    # Nature
    if (
        profile.nature_importance
        and profile.nature_importance >= 7
        and metadata.get("nature_score", 0) >= 7
    ):
        matches.append(
            "beautiful natural surroundings"
        )

    # Culture
    if (
        profile.culture_importance
        and profile.culture_importance >= 7
        and metadata.get("culture_score", 0) >= 7
    ):
        matches.append(
            "rich cultural experiences"
        )

    # Nightlife
    if (
        profile.nightlife_importance
        and profile.nightlife_importance >= 7
        and metadata.get("nightlife") == "high"
    ):
        matches.append(
            "vibrant nightlife"
        )

    return matches
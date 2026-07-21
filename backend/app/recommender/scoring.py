"""Weighted scoring engine for destination recommendations.

Design notes:
- All scoring is deterministic. The LLM never influences ranking.
- `score_candidate()` is the single source of truth for component scores.
  Both the final weighted score and the matched-feature explanations are
  derived from the SAME computed components, so they can never drift
  apart (previously each was computed independently, which risked the
  explanation text disagreeing with what actually drove the score).
"""

from dataclasses import dataclass

from app.conversation.user_profile import UserProfile
from app.models.destination import Destination
from app.recommender.candidate_search import CandidateDestination

# ---------------------------------------------------------------------------
# Weights
# ---------------------------------------------------------------------------

WEIGHTS = {
    "semantic": 0.30,
    "budget": 0.20,
    "terrain": 0.10,
    "travel_style": 0.10,
    "season": 0.10,
    "lifestyle": 0.10,
    "crowd": 0.10,
}

# ---------------------------------------------------------------------------
# Thresholds used for "is this worth mentioning as a reason" decisions.
# Pulled out as named constants so they live next to the weights they relate
# to, instead of being scattered as magic numbers through matched-feature
# logic.
# ---------------------------------------------------------------------------

SEMANTIC_STRONG_MATCH = 0.80
SEMANTIC_GOOD_MATCH = 0.65
BUDGET_FIT_THRESHOLD = 0.75
LIFESTYLE_IMPORTANCE_THRESHOLD = 7
LIFESTYLE_METADATA_THRESHOLD = 7

# Crowd levels are ordinal, not categorical — "medium" for a "low"
# preference is a softer mismatch than "high" for "low".
CROWD_LEVELS = ["low", "medium", "high"]

MONTHS = [
    "jan", "feb", "mar", "apr",
    "may", "jun", "jul", "aug",
    "sep", "oct", "nov", "dec",
]


@dataclass
class ComponentScores:
    """All individually-computed score components for one candidate.

    Computed once per candidate and reused by both `calculate_final_score`
    and `build_matched_features`, so the two can never disagree about
    what actually matched.
    """

    semantic: float
    terrain: float
    travel_style: float
    budget: float
    season: float
    lifestyle: float
    crowd: float

    terrain_overlap: set
    travel_style_overlap: set


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def metadata(destination: Destination) -> dict:
    return destination.cost_profile.get("metadata", {})


def metadata_score(destination: Destination, key: str) -> float:
    return metadata(destination).get(key, 0) / 10


# ---------------------------------------------------------------------------
# Individual component scorers
# ---------------------------------------------------------------------------

def semantic_score(candidate: CandidateDestination) -> float:
    return candidate.semantic_score


def terrain_score(profile: UserProfile, destination: Destination) -> float:
    if not profile.terrain_preferences:
        return 0.5
    overlap = set(profile.terrain_preferences).intersection(destination.terrain)
    return len(overlap) / len(profile.terrain_preferences)


def travel_style_score(profile: UserProfile, destination: Destination) -> float:
    if not profile.travel_styles:
        return 0.5
    overlap = set(profile.travel_styles).intersection(destination.travel_styles)
    return len(overlap) / len(profile.travel_styles)


def crowd_score(profile: UserProfile, destination: Destination) -> float:
    """Ordinal crowd matching: adjacent levels score better than opposite
    extremes. Exact match = 1.0, one level off = 0.5, two levels off = 0.0.
    """
    if profile.crowd_preference is None:
        return 0.5

    if profile.crowd_preference not in CROWD_LEVELS or destination.typical_crowd_level not in CROWD_LEVELS:
        # Unknown value — fall back to old binary behavior rather than crash.
        return 1.0 if profile.crowd_preference == destination.typical_crowd_level else 0.0

    distance = abs(
        CROWD_LEVELS.index(profile.crowd_preference)
        - CROWD_LEVELS.index(destination.typical_crowd_level)
    )
    return {0: 1.0, 1: 0.5, 2: 0.0}[distance]


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


def budget_score(profile: UserProfile, destination: Destination) -> float:
    """Asymmetric budget scoring.

    Being at or under budget is a good outcome and should score highly —
    a destination that costs half the user's daily budget is NOT a worse
    match than one that's exactly at budget. Only going OVER budget should
    incur a penalty, and that penalty should scale with how far over it is.

    Previous behavior used a symmetric min/max ratio, which penalized
    "way under budget" destinations exactly as harshly as "way over
    budget" ones — systematically under-ranking affordable options for
    higher-budget users.
    """
    daily_budget = get_daily_budget(profile)

    if daily_budget is None:
        return 0.5

    daily = destination.cost_profile.get("daily_cost", {})

    totals = []
    for tier in ["budget", "mid_range", "luxury"]:
        if tier not in daily:
            continue
        totals.append(sum(daily[tier].values()))

    if not totals:
        return 0.5

    # Closest available cost tier to what the user can spend.
    closest = min(totals, key=lambda x: abs(x - daily_budget))

    if closest <= daily_budget:
        # At or under budget: full credit. (Optionally could taper very
        # slightly for extreme under-spend if that correlates with a
        # worse experience tier, but we don't have data to support that
        # yet, so full credit is the safer default.)
        return 1.0

    # Over budget: decay based on how far over, capped at 0.
    overage_ratio = (closest - daily_budget) / daily_budget
    return max(0.0, 1.0 - overage_ratio)


def lifestyle_score(profile: UserProfile, destination: Destination) -> float:
    scores = []

    lifestyle_fields = [
        ("food_importance", "food_score"),
        ("culture_importance", "culture_score"),
        ("relaxation_importance", "relaxation_score"),
        ("adventure_importance", "adventure_score"),
        ("nature_importance", "nature_score"),
    ]

    for importance_field, metadata_key in lifestyle_fields:
        importance = getattr(profile, importance_field)
        if importance is not None:
            scores.append((importance / 10) * metadata_score(destination, metadata_key))

    if profile.nightlife_importance is not None:
        nightlife = metadata(destination).get("nightlife", "medium")
        mapping = {"low": 0.3, "medium": 0.7, "high": 1.0}
        scores.append((profile.nightlife_importance / 10) * mapping.get(nightlife, 0.7))

    if not scores:
        return 0.5

    return sum(scores) / len(scores)


def expand_month_range(season: str | None) -> set[str]:
    if not season:
        return set()

    season = season.strip().lower()

    if season in {"all year", "year-round", "year round"}:
        return set(MONTHS)

    if "-" not in season:
        month = season[:3]
        return {month} if month in MONTHS else set()

    start, end = season.split("-", 1)
    start = start.strip()[:3]
    end = end.strip()[:3]

    if start not in MONTHS or end not in MONTHS:
        return set()

    start_idx = MONTHS.index(start)
    end_idx = MONTHS.index(end)

    if start_idx <= end_idx:
        return set(MONTHS[start_idx:end_idx + 1])

    return set(MONTHS[start_idx:] + MONTHS[:end_idx + 1])


def season_score(profile: UserProfile, destination: Destination) -> float:
    if profile.travel_month is None:
        return 0.5

    month = profile.travel_month[:3].lower()
    best = expand_month_range(destination.best_season)
    worst = expand_month_range(destination.worst_season)

    if month in best:
        return 1.0
    if month in worst:
        return 0.0
    return 0.5


# ---------------------------------------------------------------------------
# Combined scoring — single source of truth
# ---------------------------------------------------------------------------

def score_candidate(
    profile: UserProfile,
    candidate: CandidateDestination,
) -> ComponentScores:
    """Compute every component score once. Used by both the final weighted
    score and the matched-feature explanation builder."""

    destination = candidate.destination

    return ComponentScores(
        semantic=semantic_score(candidate),
        terrain=terrain_score(profile, destination),
        travel_style=travel_style_score(profile, destination),
        budget=budget_score(profile, destination),
        season=season_score(profile, destination),
        lifestyle=lifestyle_score(profile, destination),
        crowd=crowd_score(profile, destination),
        terrain_overlap=set(profile.terrain_preferences or []) & set(destination.terrain),
        travel_style_overlap=set(profile.travel_styles or []) & set(destination.travel_styles),
    )


def calculate_final_score(components: ComponentScores) -> float:
    score = (
        components.semantic * WEIGHTS["semantic"]
        + components.budget * WEIGHTS["budget"]
        + components.terrain * WEIGHTS["terrain"]
        + components.travel_style * WEIGHTS["travel_style"]
        + components.season * WEIGHTS["season"]
        + components.lifestyle * WEIGHTS["lifestyle"]
        + components.crowd * WEIGHTS["crowd"]
    )
    return round(score, 4)


def build_matched_features(
    profile: UserProfile,
    candidate: CandidateDestination,
    components: ComponentScores,
) -> list[str]:
    """Builds human-readable matched features FROM the same components
    used for scoring — guarantees explanations never disagree with the
    actual score."""

    destination = candidate.destination
    matches = []

    if components.semantic >= SEMANTIC_STRONG_MATCH:
        matches.append("strong semantic match to the user's travel preferences")
    elif components.semantic >= SEMANTIC_GOOD_MATCH:
        matches.append("good overall match to the user's travel preferences")

    if components.terrain_overlap:
        matches.append(f"preferred terrain: {', '.join(sorted(components.terrain_overlap))}")

    if components.travel_style_overlap:
        matches.append(f"travel style: {', '.join(sorted(components.travel_style_overlap))}")

    if components.budget >= BUDGET_FIT_THRESHOLD:
        matches.append("fits the user's budget")

    if components.season == 1.0:
        matches.append(f"excellent during {profile.travel_month}")

    if profile.crowd_preference and components.crowd == 1.0:
        matches.append(f"{profile.crowd_preference} crowd levels")

    meta = metadata(destination)

    lifestyle_checks = [
        ("food_importance", "food_score", "excellent food scene"),
        ("adventure_importance", "adventure_score", "great adventure opportunities"),
        ("relaxation_importance", "relaxation_score", "ideal for relaxation"),
        ("nature_importance", "nature_score", "beautiful natural surroundings"),
        ("culture_importance", "culture_score", "rich cultural experiences"),
    ]

    for importance_field, metadata_key, message in lifestyle_checks:
        importance = getattr(profile, importance_field)
        if (
            importance
            and importance >= LIFESTYLE_IMPORTANCE_THRESHOLD
            and meta.get(metadata_key, 0) >= LIFESTYLE_METADATA_THRESHOLD
        ):
            matches.append(message)

    if (
        profile.nightlife_importance
        and profile.nightlife_importance >= LIFESTYLE_IMPORTANCE_THRESHOLD
        and meta.get("nightlife") == "high"
    ):
        matches.append("vibrant nightlife")

    return matches
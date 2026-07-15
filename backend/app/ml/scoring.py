"""
Phase 1 ranking: rule-based weighted score, not a learned model (see
Phase 1 plan -- there's no interaction data yet to train a ranker on).

Deliberately explicit about two failure modes caught before in the explorer
module rebuild:
  1. Never return early from inside a scoring loop -- every candidate must
     get a score computed independently.
  2. Raw cosine similarity is in [-1, 1] and clusters tightly near 0.6-0.9
     for related short texts; it must be rescaled before blending with the
     other 0-1 signals, or it dominates/underweights unpredictably.
"""
from app.config import settings

CROWD_LEVELS = {"low": 0, "medium": 1, "high": 2}


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def rescale_similarity(raw_cosine: float) -> float:
    """
    Maps raw cosine similarity from its observed working range (roughly
    0.3-0.9 for this embedding model on short profile/destination text)
    into a full 0-1 band, clamped at the edges. Without this, nearly every
    candidate scores 0.6-0.8 and the ranking barely differentiates them.
    """
    low, high = 0.3, 0.9
    scaled = (raw_cosine - low) / (high - low)
    return max(0.0, min(1.0, scaled))

def style_match_score(raw_cosine: float, style_tag_match: bool) -> float:
    """
    Blends semantic similarity (embedding cosine) with an explicit tag match.
    The explicit tag match is weighted higher (0.6) than the embedding score
    (0.4) because it's a direct, curated signal, whereas embedding similarity
    is comparing loosely-related description text and is noisier.
    """
    semantic = rescale_similarity(raw_cosine)
    tag_score = 1.0 if style_tag_match else 0.0
    return 0.4 * semantic + 0.6 * tag_score


def budget_fit_score(estimated_cost_inr: float, user_budget_inr: float | None) -> float:
    if user_budget_inr is None or user_budget_inr <= 0:
        return 0.5  # neutral if we don't know the user's budget yet
    if estimated_cost_inr <= user_budget_inr:
        # reward being close to budget without going over (uses full budget)
        ratio = estimated_cost_inr / user_budget_inr
        return 0.7 + 0.3 * ratio
    # over budget: score decays the further over it goes
    overage_ratio = (estimated_cost_inr - user_budget_inr) / user_budget_inr
    return max(0.0, 0.7 - overage_ratio)


def season_fit_score(destination_best_season: str, travel_months: list[str] | None) -> float:
    if not travel_months:
        return 0.5  # neutral if the user hasn't given travel dates yet
    best_months = {m.strip() for m in destination_best_season.replace("-", ",").split(",")}
    overlap = best_months.intersection(set(travel_months))
    return 1.0 if overlap else 0.4


def crowd_fit_score(destination_crowd_level: str, user_crowd_tolerance: str | None) -> float:
    if not user_crowd_tolerance:
        return 0.5
    dest_level = CROWD_LEVELS.get(destination_crowd_level, 1)
    user_level = CROWD_LEVELS.get(user_crowd_tolerance, 1)
    diff = abs(dest_level - user_level)
    return {0: 1.0, 1: 0.6, 2: 0.2}.get(diff, 0.2)


def compute_match_score(
    style_similarity_raw: float,
    style_tag_match: bool,
    estimated_cost_inr: float,
    user_budget_inr: float | None,
    destination_best_season: str,
    travel_months: list[str] | None,
    destination_crowd_level: str,
    user_crowd_tolerance: str | None,
) -> float:
    """
    Weighted blend of the four Phase 1 signals. Weights are defined once in
    config.py so they're tunable without touching scoring logic, and so this
    function and any future explanation text always agree on what mattered.
    """
    style_score = style_match_score(style_similarity_raw, style_tag_match)
    budget_score = budget_fit_score(estimated_cost_inr, user_budget_inr)
    season_score = season_fit_score(destination_best_season, travel_months)
    crowd_score = crowd_fit_score(destination_crowd_level, user_crowd_tolerance)

    total = (
        settings.weight_style_match * style_score
        + settings.weight_budget_fit * budget_score
        + settings.weight_season_fit * season_score
        + settings.weight_crowd_fit * crowd_score
    )
    return round(total, 4)

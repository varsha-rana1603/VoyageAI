"""
app/trip_planner/attractions/scorer.py

Single responsibility: compute the individual [0,1] factor scores for
one (attraction, user_profile) pair. No sorting, no filtering, no
explanation text — ranker.py owns combining these into a final score
and building the human-readable "why".

WEIGHTS is deliberately static/global for now, not per-travel-style. If
you later want e.g. "relaxation" travellers to weight popularity less
and crowd-avoidance more, swap this for a dict-of-dicts keyed by
dominant travel style rather than restructuring these functions — the
functions themselves don't need to know about weighting at all.
"""

from __future__ import annotations

import math

from .models import AttractionLike, UserProfileLike
from .travel_style_taxonomy import TRAVEL_STYLE_TAGS
from .interest_taxonomy import INTEREST_TAGS

WEIGHTS = {
    "interest_match": 0.28,
    "travel_style_match": 0.18,
    "lifestyle_match": 0.15,
    "quality": 0.12,
    "popularity": 0.08,
    "review_confidence": 0.05,
    "family_fit": 0.05,
    "budget_fit": 0.04,
    "crowd_fit": 0.05,
}

# Keyed on Attraction.importance. Confirm these are the exact strings your
# prominence-tier function writes — if it uses different labels (e.g.
# "high"/"medium"/"low"), update this dict, not the functions below.
_IMPORTANCE_SCORE = {
    "iconic": 1.0,
    "notable": 0.65,
    "local": 0.35,
}

def travel_style_match(attraction, profile):

    if not profile.travel_styles:
        return 0.5

    tags = {
        attraction.category.lower(),
        *[t.lower() for t in attraction.tags]
    }

    scores = []

    for style in profile.travel_styles:

        allowed = TRAVEL_STYLE_TAGS.get(
            style.lower(),
            set(),
        )

        overlap = len(tags & allowed)

        if not allowed:
            scores.append(0.5)

        else:
            scores.append(
                overlap / max(1, len(tags))
            )

    return min(
    1.0,
    max(scores),
)


def exploration_interest_match(attraction, profile):

    if not profile.exploration_interests:
        return 0.5

    tags = {
        attraction.category.lower(),
        *[t.lower() for t in attraction.tags]
    }

    scores = []

    for interest in profile.exploration_interests:

        allowed = INTEREST_TAGS.get(
            interest.lower(),
            set(),
        )

        overlap = len(tags & allowed)

        if not allowed:
            scores.append(0.5)

        else:
            scores.append(
                overlap / max(1, len(tags))
            )

    return min(
    1.0,
    max(scores),
)


# Maps an attraction category/tag keyword to the UserProfile importance
# field it should be judged against. Extend this dict, not the function
# below, if new categories need coverage.
_LIFESTYLE_IMPORTANCE_MAP = {
    "food": "food_importance",
    "restaurant": "food_importance",
    "market": "food_importance",
    "nightlife": "nightlife_importance",
    "bar": "nightlife_importance",
    "club": "nightlife_importance",
    "adventure": "adventure_importance",
    "outdoor": "adventure_importance",
    "sports": "adventure_importance",
    "spa": "relaxation_importance",
    "wellness": "relaxation_importance",
    "museum": "culture_importance",
    "historic": "culture_importance",
    "landmark": "culture_importance",
    "religious": "culture_importance",
    "art": "culture_importance",
    "park": "nature_importance",
    "nature": "nature_importance",
    "garden": "nature_importance",
}


def lifestyle_importance_fit(attraction: AttractionLike, profile: UserProfileLike) -> float:
    """Uses the 1-5 lifestyle importance scores, which are a stronger
    signal than a flat interest-tag match — a traveller can rate food a 5
    and nightlife a 1 even if both happen to be in their exploration_interests
    list. Attractions matching no mapped category fall back to neutral
    rather than being penalized for something the profile has no opinion on.
    """
    keys = {
    attraction.category.lower(),
    *[
        t.lower()
        for t in attraction.tags
    ]
}
    matched_fields = {_LIFESTYLE_IMPORTANCE_MAP[k] for k in keys if k in _LIFESTYLE_IMPORTANCE_MAP}
    if not matched_fields:
        return 0.5

    scores = []
    for field_name in matched_fields:
        value = getattr(profile, field_name, None)
        scores.append(0.5 if value is None else min(1.0, max(0.0, value / 5.0)))
    return sum(scores) / len(scores)

def family_friendliness(attraction, profile):

    if not profile.is_family:

        return 0.6

    if attraction.family_friendly is True:

        return 1

    if attraction.family_friendly is False:

        return 0

    return 0.4

def popularity(attraction):

    tier = _IMPORTANCE_SCORE.get(
        attraction.importance,
        0.5,
    )

    popularity_score = (
        attraction.popularity_score
        or 0.5
    )

    return (
        0.5 * tier
        +
        0.5 * popularity_score
    )


def quality(attraction):

    rating = attraction.rating or 4.0

    rating_score = rating / 5

    popularity = attraction.popularity_score or 0.5

    return min(
    1.0,
    (
        0.6 * rating_score
        +
        0.4 * popularity
    ),
)


def review_confidence(attraction: AttractionLike) -> float:
    # log-scaled with diminishing returns past ~500 reviews, rather than a
    # hard cutoff, so a 5k-review and 20k-review landmark aren't scored
    # identically "unproven" by clipping too early.
    if not attraction.review_count:
        return 0.2
    return min(1.0, math.log10(attraction.review_count + 1) / math.log10(501))


def crowd_preference_fit(attraction, profile):

    importance = popularity(attraction)

    preference = profile.crowd_preference

    if preference == "avoid_crowds":

        return 1 - importance

    if preference == "seek_popular":

        return importance

    return 0.5

def _infer_budget_sensitivity(profile: UserProfileLike) -> float:
    """Returns 0-1, higher = more budget-conscious.

    PLACEHOLDER: UserProfile has no budget_tier label, only raw
    total_budget/min/max (assumed AED). Attraction has no per-item price
    either (only is_free + an unparsed ticket_information JSONB), so there's
    nothing precise to compare a budget against yet at the attraction level.
    The AED bands below are a rough global guess, not derived from your
    destination's actual budget-tier costs.

    Replace this once the Budget Engine (Step 9 in the roadmap) exists —
    at that point compare profile budget against THIS destination's own
    generated daily-activities cost (already produced at destination
    ingestion) instead of a hardcoded global threshold, and ideally parse
    ticket_information for a real per-attraction price.
    """
    budget = profile.total_budget or profile.maximum_budget
    if not budget or not profile.duration_days:
        return 0.5  # unknown -> neutral, don't penalize paid attractions blindly
    travellers = profile.traveller_count or (profile.adults or 1) + (profile.children or 0)
    per_person_per_day = budget / max(1, profile.duration_days) / max(1, travellers)

    if per_person_per_day < 150:
        return 0.85
    if per_person_per_day < 400:
        return 0.5
    return 0.15


def budget_fit(attraction: AttractionLike, profile: UserProfileLike) -> float:
    if attraction.is_free is True:
        return 1.0
    if attraction.is_free is False:
        sensitivity = _infer_budget_sensitivity(profile)
        return round(1.0 - sensitivity * 0.6, 3)  # ranges ~0.49 (budget-conscious) to 0.91 (not)
    return 0.6  # unknown ticket status


def score_all_factors(
    attraction,
    profile,
):

    return {

        "interest_match":
            exploration_interest_match(
                attraction,
                profile,
            ),

        "travel_style_match":
            travel_style_match(
                attraction,
                profile,
            ),

        "lifestyle_match":
            lifestyle_importance_fit(
                attraction,
                profile,
            ),

        "quality":
            quality(
                attraction,
            ),

        "popularity":
            popularity(
                attraction,
            ),

        "review_confidence":
            review_confidence(
                attraction,
            ),

        "family_fit":
            family_friendliness(
                attraction,
                profile,
            ),

        "budget_fit":
            budget_fit(
                attraction,
                profile,
            ),

        "crowd_fit":
            crowd_preference_fit(
                attraction,
                profile,
            ),
    }
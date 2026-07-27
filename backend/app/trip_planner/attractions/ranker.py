"""
app/trip_planner/attractions/ranker.py

Single responsibility: the public entry point for this package.
filters.py -> scorer.py -> combine into RankedAttraction -> sort ->
explain. No I/O, no LLM calls — pure function of its inputs, same as the
destination recommendation engine.

Usage:

    from app.trip_planner.attractions.ranker import rank_attractions

    ranked = rank_attractions(
        destination_id=destination.id,
        user_profile=user_profile,
        attractions=loader.get_attractions(destination.id),
    )

NOTE on must_visit: UserProfile.must_visit is a free-text list collected
before the destination was known, so it can't be resolved to real
attraction rows here — this package only ranks attractions it was
handed. Whoever calls rank_attractions() is responsible for resolving
must_visit names to attraction IDs first (e.g. fuzzy/embedding match
against this destination's attraction names) and passing the results in
as excluded_attraction_ids' counterpart — a must-see boost/force-include
— which doesn't exist as a parameter yet. Don't assume must_visit is
already being honored just because this module runs without error.
"""

from __future__ import annotations

from uuid import UUID

from . import scorer
from .filters import filter_eligible
from .models import AttractionLike, RankedAttraction, RankingFactor, UserProfileLike

_EXPLANATION_LABELS = {
    "interest_match": "matches your interests",
    "travel_style_match": "matches your travel style",
    "lifestyle_match": "fits what matters most to you",
    "quality": "highly rated",
    "popularity": "one of the destination's highlights",
    "review_confidence": "trusted by many travellers",
    "family_fit": "great for families",
    "budget_fit": "fits your budget",
    "crowd_fit": "matches your crowd preference",
}


def _build_explanation(factors: list[RankingFactor], top_n: int = 2) -> str:
    top = sorted(factors, key=lambda f: f.contribution, reverse=True)[:top_n]
    phrases = [_EXPLANATION_LABELS.get(f.name, f.name) for f in top if f.contribution > 0]
    if not phrases:
        return "Included to round out your itinerary."
    return "Recommended: " + ", ".join(phrases) + "."


def rank_attractions(
    destination_id: UUID,
    user_profile: UserProfileLike,
    attractions: list[AttractionLike],
    excluded_attraction_ids: set | None = None,
    wheelchair_needed: bool = False,
) -> list[RankedAttraction]:
    print(f"Input attractions: {len(attractions)}")

    eligible = filter_eligible(
        attractions,
        destination_id=destination_id,
        excluded_attraction_ids=excluded_attraction_ids,
        wheelchair_needed=wheelchair_needed,
    )

    print(f"Eligible attractions: {len(eligible)}")

    ranked: list[RankedAttraction] = []
    for attraction in eligible:
        raw_scores = scorer.score_all_factors(attraction, user_profile)

        factors = [
            RankingFactor(
                name=name,
                weight=scorer.WEIGHTS[name],
                raw_score=score,
                contribution=scorer.WEIGHTS[name] * score,
            )
            for name, score in raw_scores.items()
        ]
        total_score = round(sum(f.contribution for f in factors), 4)

        ranked.append(
            RankedAttraction(
                attraction_id=attraction.id,
                name=attraction.name,
                category=attraction.category,
                score=total_score,
                factors=factors,
                latitude=attraction.latitude,
                longitude=attraction.longitude,
                visit_duration_minutes=attraction.visit_duration_minutes,
                explanation=_build_explanation(factors),
                tags=attraction.tags,
                rating=attraction.rating,
                popularity_score=attraction.popularity_score,
                family_friendly=attraction.family_friendly,
                is_free=attraction.is_free,
            )
        )

    ranked.sort(key=lambda r: r.score, reverse=True)
    return ranked
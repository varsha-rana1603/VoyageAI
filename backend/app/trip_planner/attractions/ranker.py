"""
app/trip_planner/attractions/ranker.py

Single responsibility:
filters.py -> scorer.py -> combine into RankedAttraction -> sort -> explain.

No I/O, no LLM calls — pure function.
"""

from __future__ import annotations

from uuid import UUID

from . import scorer
from .filters import filter_eligible
from .models import (
    AttractionLike,
    RankedAttraction,
    RankingFactor,
    UserProfileLike,
)


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


def _build_explanation(
    factors: list[RankingFactor],
    top_n: int = 2
) -> str:

    top = sorted(
        factors,
        key=lambda f: f.contribution,
        reverse=True
    )[:top_n]

    phrases = [
        _EXPLANATION_LABELS.get(
            f.name,
            f.name
        )
        for f in top
        if f.contribution > 0
    ]

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

        raw_scores = scorer.score_all_factors(
            attraction,
            user_profile
        )


        factors = [
            RankingFactor(
                name=name,
                weight=scorer.WEIGHTS[name],
                raw_score=score,
                contribution=scorer.WEIGHTS[name] * score,
            )
            for name, score in raw_scores.items()
        ]


        total_score = round(
            sum(
                f.contribution
                for f in factors
            ),
            4
        )


        ranked.append(
            RankedAttraction(

                attraction_id=attraction.id,

                name=attraction.name,

                category=attraction.category,

                score=total_score,

                factors=factors,

                explanation=_build_explanation(
                    factors
                ),


                latitude=attraction.latitude,

                longitude=attraction.longitude,


                visit_duration_minutes=(
                    attraction.visit_duration_minutes
                    or 120
                ),


                tags=(
                    attraction.tags
                    or []
                ),


                rating=attraction.rating,


                popularity_score=(
                    attraction.popularity_score
                    or 0
                ),


                family_friendly=attraction.family_friendly,


                is_free=attraction.is_free,


                # --------------------------
                # Intelligence Layer
                # --------------------------

                iconic_score=(
                    attraction.popularity_score
                    or 0
                ),


                destination_fit_score=0.0,


                tourist_priority_score=(
                    1.0
                    if attraction.importance == "must_visit"
                    else 0.5
                ),


                category_quality_score=0.0,


                historical_score=(
                    getattr(
                        attraction,
                        "historical_score",
                        None
                    )
                    or 0
                ),


                architecture_score=(
                    getattr(
                        attraction,
                        "architecture_score",
                        None
                    )
                    or 0
                ),


                photography_score=(
                    getattr(
                        attraction,
                        "photography_score",
                        None
                    )
                    or 0
                ),


                crowd_score=(
                    getattr(
                        attraction,
                        "crowd_score",
                        None
                    )
                    or 0
                ),


                hidden_gem_score=(
                    getattr(
                        attraction,
                        "hidden_gem_score",
                        None
                    )
                    or 0
                ),


                opening_hours=(
                    attraction.opening_hours
                    or None
                ),


                estimated_cost=(
                    getattr(
                        attraction,
                        "estimated_cost",
                        None
                    )
                    or 0
                ),


                best_visit_times=(
                    getattr(
                        attraction,
                        "best_visit_times",
                        None
                    )
                    or []
                ),


                experience_tags=(
                    getattr(
                        attraction,
                        "experience_tags",
                        None
                    )
                    or []
                ),
            )
        )


    ranked.sort(
        key=lambda r: r.score,
        reverse=True
    )

    return ranked
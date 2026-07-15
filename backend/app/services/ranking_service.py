import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ml.scoring import compute_match_score, cosine_similarity
from app.models.destination import Destination
from app.models.profile import TravellerProfile
from app.models.trip import Trip
from app.services.budget_service import budget_tier_to_inr, estimate_trip_cost


class RankingService:
    def __init__(self, db: Session):
        self.db = db

    def recommend(self, profile: TravellerProfile, limit: int = 5, user_budget_inr: float | None = None) -> list[dict]:
        if profile.profile_embedding is None:
            raise ValueError("Profile is not ready for ranking yet -- travel_style and budget_tier are required")

        # Retrieve candidates via pgvector nearest-neighbour, over-fetch a bit
        # since final ranking re-scores on more than just embedding similarity.
        candidates = self.db.scalars(
            select(Destination)
            .order_by(Destination.destination_embedding.cosine_distance(profile.profile_embedding))
            .limit(max(limit * 3, 15))
        ).all()

        # Fall back to a tier-derived estimate if no explicit numeric budget
        # was given -- otherwise budget_fit_score is neutral for everyone,
        # every time, and contributes nothing to ranking.
        effective_budget_inr = user_budget_inr
        if effective_budget_inr is None:
            effective_budget_inr = budget_tier_to_inr(
                profile.budget_tier, profile.trip_duration_days or 5
            )

        scored = []
        for destination in candidates:
            # Every candidate is scored independently -- no early return inside
            # this loop, see app/ml/scoring.py docstring for why that matters.
            raw_similarity = cosine_similarity(profile.profile_embedding, destination.destination_embedding)
            style_tag_match = bool(profile.travel_style) and profile.travel_style in destination.travel_styles
            duration_days = profile.trip_duration_days or 5  # fallback default when duration isn't captured yet
            estimated_cost = estimate_trip_cost(destination, duration_days)

            match_score = compute_match_score(
                style_similarity_raw=raw_similarity,
                style_tag_match=style_tag_match,
                estimated_cost_inr=estimated_cost,
                user_budget_inr=effective_budget_inr,
                destination_best_season=destination.best_season,
                travel_months=None,  # Phase 1: no travel-month capture yet, treated as neutral
                destination_crowd_level=destination.typical_crowd_level,
                user_crowd_tolerance=profile.crowd_tolerance,
            )

            scored.append(
                {
                    "destination": destination,
                    "match_score": match_score,
                    "estimated_cost_inr": estimated_cost,
                    "within_budget": effective_budget_inr is None or estimated_cost <= effective_budget_inr,
                    "reason": self.explain(destination, profile, match_score),
                }
            )

        scored.sort(key=lambda x: x["match_score"], reverse=True)
        top = scored[:limit]

        for item in top:
            trip = Trip(
                traveller_profile_id=profile.id,
                destination_id=item["destination"].id,
                match_score=item["match_score"],
                estimated_cost_inr=item["estimated_cost_inr"],
                within_budget=item["within_budget"],
            )
            self.db.add(trip)
        self.db.commit()

        return top

    @staticmethod
    def explain(destination: Destination, profile: TravellerProfile, match_score: float) -> str:
        """Deterministic, template-based explanation -- not an LLM call, so
        every recommendation's reasoning is reproducible and free."""
        reasons = []
        if profile.travel_style in destination.travel_styles:
            reasons.append(f"matches your {profile.travel_style} style")
        if profile.crowd_tolerance == "low" and destination.typical_crowd_level == "low":
            reasons.append("known for being uncrowded")
        if not reasons:
            reasons.append(f"strong overall fit ({match_score:.0%} match)")
        return ", ".join(reasons).capitalize()

    def recommendations_for_profile_id(self, profile_id: uuid.UUID, limit: int, user_budget_inr: float | None):
        profile = self.db.get(TravellerProfile, profile_id)
        if profile is None:
            raise ValueError(f"No traveller profile found for id {profile_id}")
        return self.recommend(profile, limit=limit, user_budget_inr=user_budget_inr)
"""
FeatureExtractor: (UserProfile, Accommodation) -> feature dict.

Pure function of its two inputs, no DB/network calls — this is what lets it
be imported identically by the offline training script and the online
FastAPI ranking path without drift between the two.
"""

import math
from dataclasses import dataclass

BRAND_TIER_ORDINAL = {
    "budget": 0,
    "midscale": 1,
    "upper_midscale": 1,
    "upscale": 2,
    "luxury": 3,
}

PERSONA_LABELS = ("luxury", "budget", "business", "family")


@dataclass
class AccommodationFeatureExtractor:
    """
    candidate_min_price / candidate_max_price / candidate_max_metro_distance_m
    come from the current candidate set at request time (or the full training
    batch's stats at training time) — normalization is always relative to
    what's actually being compared, matching how ranking works in practice.
    """
    candidate_min_price: float
    candidate_max_price: float
    candidate_max_metro_distance_m: float = 5000.0  # fallback if unknown

    def extract(self, user_profile, accommodation) -> dict[str, float]:
        f: dict[str, float] = {}

        # --- persona: multi-label membership in travel_styles, same
        #     pattern as scoring.luxury_score already uses ---
        styles = user_profile.travel_styles or []
        f["persona_luxury"] = float("luxury" in styles)
        f["persona_budget"] = float("budget" in styles or "backpacking" in styles)
        f["persona_business"] = float("business" in styles)
        f["persona_family"] = float("family" in styles)

        # --- budget: same per-night calculation as scoring.budget_score,
        budget_total = user_profile.maximum_budget or user_profile.total_budget
        duration = user_profile.duration_days
        budget_per_night = (
            budget_total / duration
            if budget_total and duration
            else None
        )

        price = accommodation.estimated_price_per_night
        f["price_per_night_norm"] = self._norm(
            price, self.candidate_min_price, self.candidate_max_price
        )
        f["price_vs_budget_per_night_ratio"] = (
            price / budget_per_night
            if price is not None and budget_per_night
            else 1.0 
        )
        f["price_within_budget_flag"] = float(
            price is not None and budget_per_night is not None
            and price <= budget_per_night
        )

        # --- hotel quality ---
        f["hotel_rating"] = float(accommodation.rating or 0.0)
        f["hotel_review_count_log"] = math.log1p(float(accommodation.review_count or 0))
        f["hotel_star_rating"] = float(accommodation.star_rating or 0.0)
        f["hotel_quality_score"] = float(accommodation.quality_score or 0.0)

        # --- brand ---
        brand_tier = (accommodation.brand_tier or "").lower()
        f["brand_tier_ordinal"] = float(BRAND_TIER_ORDINAL.get(brand_tier, 1))
        f["luxury_positioning_score"] = float(accommodation.luxury_positioning or 0.0)
        f["has_recognized_brand"] = float(bool(accommodation.brand_name))

        # --- location: numeric distances, no guessed categorical matching ---
        f["location_quality_score"] = float(accommodation.location_quality_score or 0.0)
        f["distance_from_city_center_km"] = float(accommodation.distance_from_city_center_km or 0.0)
        f["distance_to_metro_m_norm"] = self._norm(
            accommodation.distance_to_metro_m, 0, self.candidate_max_metro_distance_m
        )
        f["distance_to_main_attractions_km"] = float(accommodation.distance_to_main_attractions_km or 0.0)
        f["average_travel_time_minutes"] = float(accommodation.average_travel_time_minutes or 0.0)

        # --- amenities: real boolean columns, not string-parsed tags ---
        f["amenity_pool"] = float(bool(accommodation.pool))
        f["amenity_spa"] = float(bool(accommodation.spa))
        f["amenity_family_friendly"] = float(bool(accommodation.family_friendly))
        f["amenity_business_friendly"] = float(bool(accommodation.business_friendly))

        # --- best_for: direct enrichment-provided persona match ---
        best_for = set(x.lower() for x in (accommodation.best_for or []))
        active_personas = {p for p in PERSONA_LABELS if p in styles}
        f["best_for_matches_persona"] = float(
            bool(best_for & active_personas)
        ) if best_for and active_personas else 0.0  # neutral-low, not a
                                                       # penalty, when data
                                                       # is missing either side

        # --- semantic: placeholder, matches current scoring.semantic_score ---
        f["semantic_similarity"] = 0.5  # TODO: replace once user/hotel
                                          # embedding cosine sim is wired up

        # --- interaction features ---
        f["persona_luxury_x_luxury_positioning"] = f["persona_luxury"] * f["luxury_positioning_score"]
        f["persona_luxury_x_brand_tier"] = f["persona_luxury"] * f["brand_tier_ordinal"]
        f["persona_budget_x_price_ratio"] = f["persona_budget"] * f["price_vs_budget_per_night_ratio"]
        f["persona_business_x_business_friendly"] = f["persona_business"] * f["amenity_business_friendly"]
        f["persona_business_x_metro_distance"] = f["persona_business"] * (1 - f["distance_to_metro_m_norm"])
        f["persona_family_x_pool"] = f["persona_family"] * f["amenity_pool"]
        f["persona_family_x_family_friendly"] = f["persona_family"] * f["amenity_family_friendly"]

        return f

    @staticmethod
    def _norm(value, lo, hi):
        if value is None or hi <= lo:
            return 0.5
        return max(0.0, min(1.0, (value - lo) / (hi - lo)))
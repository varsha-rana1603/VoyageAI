"""
Phase 1 budget estimation. estimate_trip_cost multiplies the destination's
real avg_daily_cost_inr (sourced from Amadeus hotel data + a food/transport
heuristic -- see app/seed/destinations_loader.py) by trip duration. No more
Google Places price_level bucket conversion.
"""
from app.models.destination import Destination

BUDGET_TIER_DAILY_INR = {
    "low": 3000,
    "medium": 7000,
    "high": 15000,
}


def budget_tier_to_inr(budget_tier: str | None, trip_duration_days: int) -> float | None:
    """
    Converts a qualitative budget_tier into a rough total INR figure for the
    trip, used only when the user hasn't given an explicit numeric budget
    range. Returns None if budget_tier is unset or unrecognized.
    """
    daily_rate = BUDGET_TIER_DAILY_INR.get(budget_tier)
    if daily_rate is None or not trip_duration_days:
        return None
    return daily_rate * trip_duration_days


def estimate_trip_cost(destination: Destination, trip_duration_days: int) -> float:
    return round(destination.avg_daily_cost_inr * trip_duration_days, 2)


def budget_breakdown(destination: Destination, trip_duration_days: int, user_budget_inr: float | None, budget_tier: str | None) -> dict:
    estimated_cost = estimate_trip_cost(destination, trip_duration_days)
    return {
        "destination_id": destination.id,
        "trip_duration_days": trip_duration_days,
        "estimated_cost_inr": estimated_cost,
        "base_cost_inr": destination.avg_daily_cost_inr * trip_duration_days,
        "cost_per_day_inr": destination.avg_daily_cost_inr,
        "within_budget": user_budget_inr is None or estimated_cost <= user_budget_inr,
        "budget_tier": budget_tier or "unknown",
    }
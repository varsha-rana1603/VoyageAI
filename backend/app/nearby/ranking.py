# app/nearby/ranking.py
#
# Scores and ranks a destination's sights using category-dependent weight
# formulas (sightseeing cares more about popularity than proximity;
# restaurants/shopping care more about proximity than raw fame).
#
# Distance is measured from the DESTINATION CENTER, not any specific stay
# — per the architecture decision in the original feature spec: a
# traveller wants to explore the destination, not just walk around their
# hotel. Distance from a specific recommended stay is a separate concern,
# computed later in relationship.py for the "nearby to your hotel" view.

import math

# --- Distance ---------------------------------------------------------

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in kilometers."""
    R = 6371.0  # Earth's radius, km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def distance_score(distance_km: float) -> int:
    """
    Converts distance-from-destination-center into a 0-100 score.
    Calibrated for destination-scale exploration (a sight 15km away is
    still very reasonable for a day trip), NOT walking-distance amenity
    scoring like stay_enrichment.py's distance_score — different scale,
    deliberately a separate function rather than reusing that one.
    """
    if distance_km <= 2:
        return 100
    if distance_km <= 5:
        return 90
    if distance_km <= 10:
        return 75
    if distance_km <= 15:
        return 60
    return 45


# --- Popularity (Bayesian average, IMDb-style) -------------------------

def compute_popularity_scores(sights: list) -> dict:
    """
    Bayesian-weighted rating: pulls low-review-count places toward the
    batch's mean rating, so a 4.9-with-12-reviews doesn't outrank a
    4.5-with-20,000-reviews. Places with NO rating data get pulled fully
    to the mean (neutral — neither penalized nor favored for missing data).

        WR = (v / (v + m)) * R + (m / (v + m)) * C

    v = this place's review count
    R = this place's raw rating
    m = prior weight (self-calibrated per batch, see below)
    C = mean rating across the batch

    Returns { place_id: popularity_score_0_to_100 }.
    """
    rated = [s for s in sights if s.get("rating") is not None and s.get("review_count")]

    if not rated:
        # No usable rating data at all in this batch — everyone gets a
        # neutral mid score rather than crashing on an empty mean/median.
        return {s["place_id"]: 50.0 for s in sights}

    C = sum(s["rating"] for s in rated) / len(rated)

    # m self-calibrates to "typical" review count for THIS destination —
    # a busy metro's typical review count is naturally much higher than a
    # small town's, so a fixed constant would over- or under-shrink
    # depending on destination. Median (not mean) resists outlier
    # mega-attractions skewing the prior weight.
    review_counts = sorted(s["review_count"] for s in rated)
    m = review_counts[len(review_counts) // 2]
    m = max(m, 1)  # guard against a degenerate all-zero-reviews batch

    scores = {}
    for s in sights:
        v = s.get("review_count") or 0
        R = s.get("rating") if s.get("rating") is not None else C

        wr = (v / (v + m)) * R + (m / (v + m)) * C
        scores[s["place_id"]] = round((wr / 5.0) * 100, 2)  # Google ratings are out of 5

    return scores


# --- Category-dependent formula weights ---------------------------------

# Sightseeing (culture/nature): travelers go out of their way for a great
# landmark, so popularity dominates and distance barely matters.
# Food/shopping: proximity matters more day-to-day.
RANKING_WEIGHTS = {
    "culture": {"popularity": 0.60, "preference": 0.30, "distance": 0.10},
    "nature": {"popularity": 0.60, "preference": 0.30, "distance": 0.10},
    "food": {"popularity": 0.40, "preference": 0.30, "distance": 0.30},
    "shopping": {"popularity": 0.40, "preference": 0.30, "distance": 0.30},
}


def rank_sights(
    sights: list,
    category_weights: dict,
    destination_lat: float,
    destination_lon: float,
) -> list:
    """
    Scores and ranks a destination's sights.

    `sights`: normalized dicts from google_places_provider.py
    `category_weights`: output of preference_engine.compute_category_weights()

    Returns the same sight dicts, each augmented with:
        - distance_km, distance_score
        - popularity_score
        - preference_score
        - final_score
    sorted descending by final_score.
    """
    popularity_scores = compute_popularity_scores(sights)

    ranked = []
    for sight in sights:
        category = sight.get("category", "culture")
        weights = RANKING_WEIGHTS.get(category, RANKING_WEIGHTS["culture"])

        dist_km = round(
            haversine_km(destination_lat, destination_lon, sight["lat"], sight["lon"]), 2
        )
        dist_score = distance_score(dist_km)

        pop_score = popularity_scores.get(sight["place_id"], 50.0)

        # category_weights sum to 1 across 4 categories (e.g. nature-dominant
        # user: nature=0.86, others~0.04 each) — already a reasonable 0-100-ish
        # spread once multiplied by 100, no further rescaling needed.
        pref_score = round(category_weights.get(category, 0.25) * 100, 2)

        final = (
            weights["popularity"] * pop_score
            + weights["preference"] * pref_score
            + weights["distance"] * dist_score
        )

        enriched = {
            **sight,
            "distance_km": dist_km,
            "distance_score": dist_score,
            "popularity_score": pop_score,
            "preference_score": pref_score,
            "final_score": round(final, 2),
        }
        ranked.append(enriched)

    ranked.sort(key=lambda s: s["final_score"], reverse=True)
    return ranked


if __name__ == "__main__":
    from app.nearby.sight_cache import get_sights_for_destination
    from app.nearby.preference_engine import compute_category_weights

    dest_lat, dest_lon = 28.6139, 77.2090  # Delhi

    sights = get_sights_for_destination("Delhi", lat=dest_lat, lon=dest_lon)

    weights = compute_category_weights(
        travel_style="Cultural",
        budget="medium",
        crowd_tolerance="medium",
        terrain="city",
        free_text="I want to explore history and architecture",
    )
    print("Category weights:", weights, "\n")

    ranked = rank_sights(sights, weights, dest_lat, dest_lon)

    print(f"Top 10 of {len(ranked)} ranked sights:\n")
    for s in ranked[:10]:
        print(
            f"[{s['category']:9}] {s['name']:35} "
            f"final={s['final_score']:6.2f}  "
            f"pop={s['popularity_score']:6.2f}  "
            f"pref={s['preference_score']:6.2f}  "
            f"dist={s['distance_km']:5.1f}km"
        )
    from collections import Counter
    print(Counter(s["category"] for s in ranked))
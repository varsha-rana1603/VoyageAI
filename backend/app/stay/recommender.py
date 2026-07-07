from app.destinations.user_profile import build_user_profile
from app.models import embedding_model

from app.stay.stay_search import fetch_stay
from app.stay.stay_enrichment import enrich_stay
from app.stay.stay_embeddings import embed_stays
from app.stay.stay_ranking import rank_stays
from app.stay.stay_recommendation import build_recommendation


def get_stay_recommendations(
    destination_name: str,
    travel_style: str,
    budget: str,
    crowd_tolerance: str,
    terrain: str,
    free_text: str = "",
):
    """
    Complete Stay Recommendation Pipeline

    1. Fetch and normalize nearby stays
    2. Enrich stays with heuristic scores
    3. Generate stay embeddings
    4. Build user profile
    5. Generate user embedding
    6. Rank stays
    7. Convert to frontend recommendations
    """

    # -------------------------------------------------------
    # Step 1 — Fetch nearby stays
    # fetch_stay() already normalizes stay data
    # -------------------------------------------------------

    stays = fetch_stay(destination_name)

    # print("STAYS", stays)

    if not stays:
        return []

    # -------------------------------------------------------
    # Step 2 — Enrich stays with heuristic scores
    # -------------------------------------------------------

    stays = [
        enrich_stay(
            stay,
            region_type=terrain
        )
        for stay in stays
    ]

    # print("Enriched stays", stays)

    # -------------------------------------------------------
    # Step 3 — Generate embeddings
    # -------------------------------------------------------

    stays = embed_stays(stays)

    if not stays:
        return []

    # -------------------------------------------------------
    # Step 4 — Build user profile
    # -------------------------------------------------------

    user_profile, user_text = build_user_profile(
        travel_style=travel_style,
        budget=budget,
        crowd_tolerance=crowd_tolerance,
        terrain=terrain,
        free_text=free_text,
    )

    # -------------------------------------------------------
    # Step 5 — Generate user embedding
    # -------------------------------------------------------

    user_embedding = embedding_model.encode(user_text)

    # -------------------------------------------------------
    # Step 6 — Rank stays
    # -------------------------------------------------------

    # ranked_stays = rank_stays(
    #     stays=stays,
    #     user_profile=user_profile,
    #     user_embedding=user_embedding,
    # )

    # print("Ranked stays", ranked_stays)

    # -------------------------------------------------------
    # Step 7 — Convert to frontend format
    # -------------------------------------------------------

    ranked_stays = rank_stays(
    stays=stays,
    user_profile=user_profile,
    user_embedding=user_embedding,
)

    # Normalize scores relative to the best stay
    best_score = ranked_stays[0]["scores"]["final_score"]

    for stay in ranked_stays:
        stay["scores"]["match_percentage"] = round(
            stay["scores"]["final_score"] / best_score * 100
        )

    recommendations = [
        build_recommendation(
            stay,
            user_profile,
        )
        for stay in ranked_stays
    ]
        # print("Recommendations", recommendations)

    return recommendations


if __name__ == "__main__":

    recommendations = get_stay_recommendations(
        destination_name="Manali",
        travel_style="Adventure",
        budget="Medium",
        crowd_tolerance="Avoid",
        terrain="Mountains",
        free_text="I want a peaceful stay with mountain views and nearby cafés."
    )

    from pprint import pprint

    pprint(len(recommendations))
from app.destinations.user_profile import build_user_profile
from app.models import embedding_model

from app.stay.stay_search import (
    fetch_stay,
    filter_stays,
    get_cached_stays,
    save_stays
)

from app.stay.stay_enrichment import (
    enrich_stays_with_surroundings
)

from app.stay.poi_scoring import (
    compute_category_scores
)

from app.stay.geocoder import geocode

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
    progress_callback=None,
):


    def update(stage, message, progress):

        if progress_callback:

            progress_callback({
                "stage": stage,
                "message": message,
                "progress": progress
            })


    # -------------------------
    # 1. CHECK CACHE
    # -------------------------

    update(
        "searching",
        f"Finding stays in {destination_name}...",
        10
    )


    stays = get_cached_stays(
        destination_name
    )


    # old cache protection
    if stays:

        required_fields = [
            "food_score",
            "culture_score",
            "nature_score"
        ]


        if not all(
            field in stays[0]
            for field in required_fields
        ):

            print(
                "Old cache detected. Refreshing..."
            )

            stays = []



    if stays:

        print(
            "Using cached stays:",
            len(stays)
        )


    else:


        print(
            "Creating fresh stay dataset..."
        )


        # -------------------------
        # FETCH HOTELS ONLY
        # -------------------------

        stays = fetch_stay(
            destination_name
        )


        stays = filter_stays(
            stays
        )


        if not stays:
            return []



        # -------------------------
        # DESTINATION POI ANALYSIS
        # ONLY ONE GEOAPIFY CALL
        # -------------------------

        update(
            "enriching",
            "Analyzing destination experiences...",
            25
        )


        coords = geocode(
            destination_name
        )


        destination_scores = compute_category_scores(
            lat=coords["lat"],
            lon=coords["lon"],
            radius_m=5000
        )


        print(
            "Destination scores:",
            destination_scores
        )



        # attach same destination context
        # to every stay

        stays = enrich_stays_with_surroundings(
            stays,
            destination_scores
        )



        save_stays(
            destination_name,
            stays
        )


        print(
            "Saved:",
            len(stays)
        )



    if not stays:
        return []



    # -------------------------
    # EMBEDDINGS
    # -------------------------

    update(
        "embedding",
        "Understanding stay characteristics...",
        40
    )


    stays = embed_stays(
        stays
    )


    if not stays:
        return []



    # -------------------------
    # USER PROFILE
    # -------------------------

    update(
        "profile",
        "Building your travel profile...",
        55
    )


    user_profile, user_text = build_user_profile(
        travel_style=travel_style,
        budget=budget,
        crowd_tolerance=crowd_tolerance,
        terrain=terrain,
        free_text=free_text,
    )



    # -------------------------
    # RANKING
    # -------------------------

    update(
        "matching",
        "Matching stays...",
        70
    )


    user_embedding = embedding_model.encode(
        user_text
    )


    ranked_stays = rank_stays(
        stays=stays,
        user_profile=user_profile,
        user_embedding=user_embedding
    )


    if not ranked_stays:
        return []



    # -------------------------
    # SCORE NORMALIZATION
    # -------------------------

    update(
        "ranking",
        "Calculating final match scores...",
        85
    )


    scores = [
        stay["scores"]["final_score"]
        for stay in ranked_stays
    ]


    best = max(scores)
    worst = min(scores)


    difference = (
        best - worst
        if best != worst
        else 1
    )


    for stay in ranked_stays:

        raw = stay["scores"]["final_score"]

        stay["scores"]["final_score"] = round(
            55 +
            ((raw - worst) / difference) * 42,
            2
        )



    # -------------------------
    # RESPONSE
    # -------------------------

    update(
        "finalizing",
        "Preparing recommendations...",
        95
    )


    recommendations = [

        build_recommendation(
            stay,
            user_profile
        )

        for stay in ranked_stays

    ]


    update(
        "complete",
        "Your personalized stays are ready.",
        100
    )


    return recommendations
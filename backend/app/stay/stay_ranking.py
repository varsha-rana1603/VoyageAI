from sentence_transformers import util


def budget_score(user_budget, stay_budget):

    if user_budget == stay_budget:
        return 100

    if (
        (user_budget == "budget" and stay_budget == "mid")
        or
        (user_budget == "mid" and stay_budget == "budget")
    ):
        return 75

    if (
        (user_budget == "mid" and stay_budget == "luxury")
        or
        (user_budget == "luxury" and stay_budget == "mid")
    ):
        return 75

    return 40


def rating_score(rating):

    if rating is None:
        return 70

    return rating * 20


def amenity_score(stay):

    scores = [
        stay["food_score"],
        stay["tourism_score"],
        stay["shopping_score"],
        stay["connectivity_score"],
        stay["nature_score"],
    ]

    return sum(scores) / len(scores)


def rank_stays(stays, user_profile, user_embedding):

    ranked = []

    for stay in stays:

        semantic = (
            util.cos_sim(
                user_embedding,
                stay["embedding"]
            ).item()
            * 100
        )

        budget = budget_score(
            user_profile["budget_level"],
            stay["price_level"]
        )

        rating = rating_score(
            stay["rating"]
        )

        distance = stay["distance_score"]

        amenities = amenity_score(
            stay
        )

        final = (
            semantic * 0.40
            + budget * 0.20
            + rating * 0.15
            + distance * 0.15
            + amenities * 0.10
        )

        stay["scores"] = {

            "semantic_score": round(semantic, 2),

            "budget_score": budget,

            "rating_score": round(rating, 2),

            "distance_score": distance,

            "amenity_score": round(amenities, 2),

            "final_score": round(final, 2),

        }

        ranked.append(stay)

    ranked.sort(
        key=lambda x: x["scores"]["final_score"],
        reverse=True
    )

    return ranked[:10]
from sentence_transformers import util


def budget_score(user_budget, stay_budget):

    # normalize naming
    user_budget = user_budget.lower()
    stay_budget = stay_budget.lower()

    if user_budget == "mid":
        user_budget = "medium"

    if stay_budget == "mid":
        stay_budget = "medium"


    if user_budget == stay_budget:
        return 100


    if (
        (user_budget == "budget" and stay_budget == "medium")
        or
        (user_budget == "medium" and stay_budget == "budget")
    ):
        return 75


    if (
        (user_budget == "medium" and stay_budget == "luxury")
        or
        (user_budget == "luxury" and stay_budget == "medium")
    ):
        return 75


    return 40



def rating_score(rating):

    if rating is None:
        return 70

    return min(rating * 20, 100)



def amenity_score(stay):

    scores = [
        stay.get("food_score", 0),
        stay.get("culture_score", 0),
        stay.get("shopping_score", 0),
        stay.get("connectivity_score", 0),
        stay.get("nature_score", 0),
        stay.get("adventure_score", 0),
    ]

    return sum(scores) / len(scores)



def rank_stays(stays, user_profile, user_embedding):

    ranked = []


    for stay in stays:


        # Semantic similarity from free text
        semantic = (
            util.cos_sim(
                user_embedding,
                stay["embedding"]
            ).item()
            * 100
        )


        budget = budget_score(
            user_profile["budget_level"],
            stay.get("price_level", "medium")
        )


        rating = rating_score(
            stay.get("rating")
        )


        distance = stay.get(
            "distance_score",
            50
        )


        # Surrounding features
        food = stay.get("food_score", 0)
        shopping = stay.get("shopping_score", 0)
        culture = stay.get("culture_score", 0)
        nature = stay.get("nature_score", 0)
        adventure = stay.get("adventure_score", 0)
        connectivity = stay.get("connectivity_score", 0)


        surroundings = (
            0.25 * food +
            0.15 * shopping +
            0.15 * culture +
            0.20 * nature +
            0.10 * adventure +
            0.15 * connectivity
        )


        final = (
            0.30 * semantic +
            0.25 * surroundings +
            0.15 * budget +
            0.10 * rating +
            0.20 * distance
        )


        amenities = amenity_score(stay)


        stay["scores"] = {

            "semantic_score": round(semantic, 2),

            "food_score": round(food, 2),

            "culture_score": round(culture, 2),

            "nature_score": round(nature, 2),

            "adventure_score": round(adventure, 2),

            "connectivity_score": round(connectivity, 2),

            "shopping_score": round(shopping, 2),

            "budget_score": round(budget, 2),

            "distance_score": round(distance, 2),

            "rating_score": round(rating, 2),

            "amenity_score": round(amenities, 2),

            "final_score": round(final, 2),
        }


        ranked.append(stay)



    ranked.sort(
        key=lambda x: x["scores"]["final_score"],
        reverse=True
    )


    return ranked[:10]
def get_confidence(score):
    print("SCORE",score)
    if score >= 90:
        return "Excellent Match", "95%+"

    if score >= 80:
        return "Great Match", "85–95%"

    if score >= 70:
        return "Good Match", "75–85%"

    return "Worth Considering", "<75%"

def generate_reasons(stay, scores, user):

    reasons = []

    if scores["budget_score"] >= 90:
        reasons.append(
            f"Fits your {user['budget_level']} budget."
        )

    if scores["semantic_score"] >= 90:
        reasons.append(
            "Matches your travel style."
        )

    if scores["distance_score"] >= 90:
        reasons.append(
            "Located close to the town centre."
        )

    if scores["amenity_score"] >= 80:
        reasons.append(
            "Excellent nearby cafés and attractions."
        )

    if scores["rating_score"] >= 90:
        reasons.append(
            "Highly rated by travelers."
        )

    return reasons

def generate_pros(stay):

    pros = []

    if stay["nature_score"] > 85:
        pros.append("Beautiful natural surroundings")

    if stay["food_score"] > 80:
        pros.append("Great nearby cafés")

    if stay["tourism_score"] > 80:
        pros.append("Close to major attractions")

    if stay["distance_score"] > 80:
        pros.append("Convenient location")

    if stay["connectivity_score"] > 80:
        pros.append("Easy transport access")

    return pros

def generate_cons(stay):

    cons = []

    if stay["distance_score"] < 60:
        cons.append(
            "Far from the town centre"
        )

    if stay["food_score"] < 60:
        cons.append(
            "Limited nearby dining options"
        )

    if stay["shopping_score"] < 60:
        cons.append(
            "Few nearby shops"
        )

    if stay["connectivity_score"] < 60:
        cons.append(
            "Limited transport connectivity"
        )

    return cons

def build_recommendation(stay, user):

    scores = stay["scores"]
    print("SCORES:",scores)
    confidence, percentage = get_confidence(
        scores["final_score"]
    )

    return {

        "id": stay["id"],

        "name": stay["name"],

        "type": stay["type"],

        "address": stay["address"],

        "rating": stay["rating"],

        "website": stay["website"],

        "phone": stay["phone"],

        "price_level": stay["price_level"],

        "distance_from_center": stay["distance_from_center"],

        "confidence": confidence,

        "match_percentage": percentage,

        "reasons": generate_reasons(
            stay,
            scores,
            user
        ),

        "pros": generate_pros(
            stay
        ),

        "cons": generate_cons(
            stay
        ),

        "ranking_breakdown": {

            "semantic": scores["semantic_score"],

            "budget": scores["budget_score"],

            "rating": scores["rating_score"],

            "distance": scores["distance_score"],

            "amenities": scores["amenity_score"],

            "overall": scores["final_score"],
        },
    }
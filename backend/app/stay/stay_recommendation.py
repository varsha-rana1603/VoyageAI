def get_confidence(score):
    # print("SCORE",score)
    if score >= 90:
        return "Excellent Match", "95%+"

    if score >= 80:
        return "Great Match", "85–95%"

    if score >= 70:
        return "Good Match", "75–85%"

    return "Worth Considering", "<75%"

def generate_reasons(stay, scores, user):

    reasons = []

    if scores["budget_score"] >= 80:
        reasons.append(
            f"Fits your {user['budget_level']} budget."
        )

    if scores["food_score"] >= 80:
        reasons.append(
            "Great cafés and restaurants nearby."
        )

    if scores["distance_score"] >= 90:
        reasons.append(
            "Located close to the city centre."
        )

    if scores["nature_score"] >= 80:
        reasons.append(
            "Beautiful natural surroundings."
        )

    if scores["culture_score"] >= 80:
        reasons.append(
            "Close to attractions and cultural places."
        )

    return reasons[:4]

def generate_pros(stay):

    pros = []

    if stay.get("nature_score",0) > 85:
        pros.append(
            "Beautiful natural surroundings"
        )

    if stay.get("food_score",0) > 80:
        pros.append(
            "Great nearby cafés and restaurants"
        )

    if stay.get("culture_score",0) > 80:
        pros.append(
            "Close to major attractions"
        )

    if stay.get("distance_score",0) > 80:
        pros.append(
            "Convenient location"
        )

    if stay.get("connectivity_score",0) > 80:
        pros.append(
            "Easy transport access"
        )

    return pros

def generate_cons(stay):

    cons = []

    if stay.get("distance_score",0) < 60:
        cons.append(
            "Far from the city centre"
        )

    if stay.get("food_score",0) < 60:
        cons.append(
            "Limited dining options nearby"
        )

    if stay.get("shopping_score",0) < 60:
        cons.append(
            "Few shopping options nearby"
        )

    if stay.get("connectivity_score",0) < 60:
        cons.append(
            "Limited transport connectivity"
        )

    return cons

def build_recommendation(stay, user):

    scores = stay["scores"]
    # print("SCORES:",scores)
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

    "overall": scores["final_score"],

    "food": stay.get(
        "food_score",
        50
    ),

    "budget": stay.get(
        "budget_score",
        50
    ),

    "location": stay.get(
        "distance_score",
        50
    ),

    "nature": stay.get(
        "nature_score",
        50
    ),

    "culture": stay.get(
        "culture_score",
        50
    ),

    "adventure": stay.get(
        "adventure_score",
        50
    ),

    "connectivity": stay.get(
        "connectivity_score",
        50
    ),

    "shopping": stay.get(
        "shopping_score",
        50
    )
},
    }
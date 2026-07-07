#converts scored into user-friendly outputs

#Converts the final numeric score into a user-friendly confidence label
def get_confidence(final_score):  
    if final_score >= 90:
        return "Excellent Match", "95%+"
    elif final_score >= 80:
        return "Great Match", "85-95%"
    elif final_score >= 70:
        return "Good Match", "75-85%"
    elif final_score >= 60:
        return "Worth Considering","65-75%"
    else:
        return "Explore if interested", "<65%"
    
#Generate why we recommend it
def generate_reasons(destination, scores, user_profile):
    reasons = []

    #Terrain
    if scores["terrain_score"] == 100:
        reasons.append(
            f"Matches your preferred {user_profile['terrain']} destination."
        )
    #Budget
    if scores["budget_score"] >= 100:
        reasons.append(
            f"Fits your {user_profile['budget_level']} budget."
        )
    elif scores["budget_score"] >= 70:
        reasons.append(
            "close to your preferred budget."
        )
    #Crowd
    if scores["crowd_score"] >= 100:
        reasons.append(
            "Matches your crowd preference."
        )

    #Preference
    if scores["preference_score"] >= 90:
        reasons.append(
            "Excellent match for your travel style."
        )
    elif scores["preference_score"] >= 75:
        reasons.append(
            "Good match for your travel style."
        )
    
    #Semantic
    if scores["semantic_score"] >= 45:
        reasons.append(
            "Strong semantic match with your travel description."
        )

    return reasons

def generate_pros(destination):
    pros = []

    if destination["crowd_level"] == "low":
        pros.append("Peaceful atmosphere")

    if destination["budget_level"] == "low":
        pros.append("Budget friendly")

    if destination["budget_level"] == "medium":
        pros.append("Good value for money")

    if destination["region_type"] == "mountains":
        pros.append("Beautiful mountain scenery")

    elif destination["region_type"] == "beach":
        pros.append("Relaxing beaches")

    elif destination["region_type"] == "city":
        pros.append("Plenty of attractions")

    elif destination["region_type"] == "forest":
        pros.append("Rich natural surroundings")

    return pros

def generate_cons(destination):

    cons = []

    if destination["crowd_level"] == "high":
        cons.append("Can get crowded during peak season")

    if destination["budget_level"] == "luxury":
        cons.append("Higher travel expenses")

    if destination["region_type"] == "mountains":
        cons.append("Travel may involve long road journeys")

    if destination["region_type"] == "desert":
        cons.append("Very hot during summer")

    return cons

#Build the final recommendation
def build_recommendation(destination, scores, user_profile):

    confidence_label, confidence_percent = get_confidence(
        scores["final_score"]
    )

    return {
    "name": str(destination["name"]),
    "state": str(destination["state"]),
    "description": str(destination["description"]),

    # Scores
    "final_score": float(round(float(scores["final_score"]), 2)),
    "semantic_score": float(round(float(scores["semantic_score"]), 2)),
    "budget_score": int(scores["budget_score"]),
    "crowd_score": int(scores["crowd_score"]),
    "terrain_score": int(scores["terrain_score"]),
    "preference_score": float(round(float(scores["preference_score"]), 2)),

    "confidence": str(confidence_label),
    "match_percentage": str(confidence_percent),

    "reasons": generate_reasons(destination, scores, user_profile),
    "pros": generate_pros(destination),
    "cons": generate_cons(destination),

    "ranking_breakdown": {
        "semantic": float(round(float(scores["semantic_score"]), 2)),
        "budget": int(scores["budget_score"]),
        "crowd": int(scores["crowd_score"]),
        "terrain": int(scores["terrain_score"]),
        "preferences": float(round(float(scores["preference_score"]), 2)),
        "overall": float(round(float(scores["final_score"]), 2)),
    },
}
#computes scores by comparing the dataset and the user's data

import numpy as np

#Budget Matching
budget_order = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "luxury": 4
}

def budget_match(user_budget, destination_budget):   #Returns a score between 0 and 100
    u = budget_order[user_budget]
    d = budget_order[destination_budget]

    difference = abs(u - d)

    if difference == 0:
        return 100
    elif difference == 1:
        return 70
    elif difference == 2:
        return 40
    else:
        return 10
    

#CROWD MATCHING
crowd_order = {
    "low": 1,
    "medium": 2,
    "high": 3
}

def crowd_match(user_crowd,destination_crowd):

    u = crowd_order[user_crowd]
    d = crowd_order[destination_crowd]

    difference = abs (u - d)

    if difference == 0:
        return 100
    elif difference == 1:
        return 60
    else: 
        return 10
    

#TERRAIN MATCHING

def terrain_match(user_terrain, destination_terrain):

    user = user_terrain.lower().rstrip("s")
    destination = destination_terrain.lower().rstrip("s")

    if user == destination:
        return 100
    
    return 0

#PREFERENCE MATCHING
PREFERENCE_COLUMNS = [
    "adventure_score",
    "nature_score",
    "luxury_score",
    "nightlife_score",
    "culture_score",
    "food_scene_score",
    "family_friendly_score"
]

def preference_match(user_profile, destination):
    differences = []

    for feature in PREFERENCE_COLUMNS:
        diff = abs(
            user_profile[feature] - destination[feature]
        )
        differences.append(diff)

    average_difference = np.mean(differences)
    score = 100 - (average_difference * 10)

    return max(score, 0)

#FINAL HYBRID SCORE

def calculate_final_score(
        semantic_score,   # now expected to already be 0-100, not raw cosine similarity
        user_profile,
        destination
):
    budget_score = budget_match(
        user_profile["budget_level"],
        destination["budget_level"]
    )

    crowd_score = crowd_match(
        user_profile["desired_crowd_level"],
        destination["crowd_level"]
    )

    terrain_score = terrain_match(
        user_profile["terrain"],
        destination["region_type"]
    )

    preference_score = preference_match(
        user_profile,
        destination
    )

    final_score = (
        0.45 * semantic_score +
        0.20 * preference_score +
        0.15 * budget_score +
        0.10 * crowd_score +
        0.10 * terrain_score
    )

    return {
        "semantic_score": semantic_score,
        "budget_score": budget_score,
        "crowd_score": crowd_score,
        "terrain_score": terrain_score,
        "preference_score": preference_score,
        "final_score": round(final_score, 2)
    }

def normalize_similarities(destinations, key="semantic_similarity"):
    scores = [d[key] for d in destinations]
    lo, hi = min(scores), max(scores)
    span = hi - lo if hi != lo else 1  # avoid divide-by-zero if all identical

    for d in destinations:
        d["semantic_score"] = round(((d[key] - lo) / span) * 100, 2)

    return destinations
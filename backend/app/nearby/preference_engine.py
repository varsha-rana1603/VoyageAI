# Converts a user's profile (structured quiz answers + free text) into
# CategoryWeights — how much they care about culture/nature/food/shopping
# sights specifically, so sightseeing_ranking.py can prioritize accordingly.

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.models import embedding_model
from app.destinations.user_profile import build_user_profile

ANCHOR_SENTENCES = {
    "culture": "exploring museums, historical landmarks, temples, monuments, architecture and cultural heritage sites",
    "nature": "peaceful natural scenery, parks, gardens, mountains, hiking trails and outdoor experiences away from crowds",
    "food": "discovering local cuisine, restaurants, cafes, street food and food markets",
    "shopping": "shopping malls, local markets, boutiques and browsing for souvenirs and goods",
}

SOFTMAX_TEMPERATURE = 0.08 #Softmax temp: LOWER = sharper differences between categories: HIGHER = closer to uniform
UNIFORM_FLOOR_WEIGHT = 0.15 
anchor_embeddings = None

def get_anchor_embeddings() -> dict:
    global anchor_embeddings
    if anchor_embeddings is None:
        anchor_embeddings = {
            category: embedding_model.encode(text)
            for category, text in ANCHOR_SENTENCES.items()
        }
    return anchor_embeddings

def softmax(values: list, temperature: float) -> np.ndarray:
    arr = np.array(values) / temperature
    arr = arr - np.max(arr)
    exp = np.exp(arr)
    return exp / exp.sum()

def compute_category_weights(
        travel_style: str,
        budget: str,
        crowd_tolerance: str,
        terrain: str,
        free_text: str = ""
) -> dict:
    #Returns weights summing to 1
    _,user_text = build_user_profile(
        travel_style=travel_style,
        budget=budget,
        crowd_tolerance=crowd_tolerance,
        terrain=terrain,
        free_text=free_text
    )
    user_embedding = embedding_model.encode(user_text)
    anchors = get_anchor_embeddings()
    categories = list(ANCHOR_SENTENCES.keys())
    similarities = [
        float(cosine_similarity([user_embedding], [anchors[cat]])[0][0])
        for cat in categories
    ]
    softmax_weights = softmax(similarities,temperature=SOFTMAX_TEMPERATURE)
    uniform = np.array([1 / len(categories)] * len(categories))
    blended = (1 - UNIFORM_FLOOR_WEIGHT) * softmax_weights + UNIFORM_FLOOR_WEIGHT * uniform
    return {
        category: round(float(weight), 4)
        for category, weight in zip(categories, blended)
    }

if __name__ == "__main__":
    print("User 1: peaceful honeymoon, mountains, avoids crowds")
    weights_1 = compute_category_weights(
        travel_style="Relaxed",
        budget="medium",
        crowd_tolerance="avoid",
        terrain="mountains",
        free_text="I want a peaceful honeymoon surrounded by nature",
    )
    for category, weight in sorted(weights_1.items(), key=lambda x: -x[1]):
        print(f"  {category:10} {weight}")
    print(f"  Expected ordering: nature > culture > food > shopping\n")
 
    print("User 2: history and architecture")
    weights_2 = compute_category_weights(
        travel_style="Cultural",
        budget="medium",
        crowd_tolerance="medium",
        terrain="city",
        free_text="I want to explore history and architecture",
    )
    for category, weight in sorted(weights_2.items(), key=lambda x: -x[1]):
        print(f"  {category:10} {weight}")
    print(f"  Expected ordering: culture should be clearly on top\n")
 

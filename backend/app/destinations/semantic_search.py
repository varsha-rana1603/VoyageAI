# app/semantic_search.py

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .user_profile import build_user_profile
from app.destinations.ranking import calculate_final_score
from .recommendation_formatter import build_recommendation


model = SentenceTransformer("all-MiniLM-L6-v2")

df = pd.read_csv("data/destinations_processed.csv")
destination_embeddings = np.load("data/destination_embeddings.npy")


def get_user_embedding(user_text: str):
    return model.encode(user_text)


def normalize_similarities(candidates, key="semantic_similarity"):
    """Rescales raw similarity scores within this candidate batch to a 0-100 range."""
    scores = [c[key] for c in candidates]
    lo, hi = min(scores), max(scores)
    span = hi - lo if hi != lo else 1  # avoid divide-by-zero if all candidates are identical

    for c in candidates:
        c["semantic_score"] = round(((c[key] - lo) / span) * 100, 2)

    return candidates


def retrieve_similar_destinations(
    user_embedding,
    numeric_profile,
    top_k=10,
):
    similarities = cosine_similarity(
        [user_embedding],
        destination_embeddings,
    )[0]

    candidate_indices = np.argsort(similarities)[::-1][:20]

    # First pass: collect raw similarity per candidate, without scoring yet
    candidates = [
        {
            "idx": idx,
            "semantic_similarity": similarities[idx],
        }
        for idx in candidate_indices
    ]

    # Normalize across this batch so the best match in THIS result set
    # reads close to 100%, rather than being capped by raw cosine similarity's typical range
    candidates = normalize_similarities(candidates)

    recommendations = []

    for c in candidates:
        destination = df.iloc[c["idx"]]

        ranking = calculate_final_score(
            c["semantic_score"],
            numeric_profile,
            destination,
        )

        recommendation = build_recommendation(
            destination,
            ranking,
            numeric_profile,
        )

        recommendations.append(recommendation)

    recommendations.sort(
        key=lambda x: x["final_score"],
        reverse=True,
    )

    return recommendations[:top_k]


def get_recommendations(
    travel_style,
    budget,
    crowd_tolerance,
    terrain,
    free_text,
    top_k=10,
):
    numeric_profile, user_text = build_user_profile(
        travel_style=travel_style,
        budget=budget,
        crowd_tolerance=crowd_tolerance,
        terrain=terrain,
        free_text=free_text,
    )

    # print("USER PROFILE", user_text)

    user_embedding = get_user_embedding(user_text)

    return retrieve_similar_destinations(
        user_embedding=user_embedding,
        numeric_profile=numeric_profile,
        top_k=top_k,
    )


if __name__ == "__main__":

    recommendations = get_recommendations(
        travel_style="adventure",
        budget="medium",
        crowd_tolerance="avoid",
        terrain="mountain",
        free_text="Quiet mountain area with shopping nearby.",
    )

    print("\nTop Recommendations\n")

    for i, r in enumerate(recommendations, start=1):
        print("=" * 70)
        print(f"{i}. {r['name']} ({r['state']})")
        print(f"{r['confidence']} • {r['match_percentage']} Match")

        print("\nWhy VoyageAI recommends this destination:")
        for reason in r["reasons"]:
            print(f"✓ {reason}")

        print("\nPros:")
        for pro in r["pros"]:
            print(f"✓ {pro}")

        print("\nThings to know:")
        for con in r["cons"]:
            print(f"• {con}")

        print("\nDescription:")
        print(r["description"])

        print("\nRanking Breakdown:")
        for key, value in r["ranking_breakdown"].items():
            print(f"{key:20}: {value}")

        print("=" * 70)
        print()
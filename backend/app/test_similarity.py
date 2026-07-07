import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("data/destinations_processed.csv")
embeddings = np.load("data/destination_embeddings.npy")

def most_similar(destination_name, top_n=5):
    idx = df[df['name'] == destination_name].index[0]
    target_vector = embeddings[idx].reshape(1, -1)
    
    similarities = cosine_similarity(target_vector, embeddings)[0]
    
    # Get top N most similar (excluding itself)
    similar_indices = similarities.argsort()[::-1][1:top_n+1]
    
    print(f"\nMost similar to {destination_name}:")
    for i in similar_indices:
        print(f"  {df.iloc[i]['name']} (score: {similarities[i]:.3f})")

most_similar("Kalpa")
most_similar("Goa")
most_similar("Hampi")
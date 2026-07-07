import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np

# Load the dataset
df = pd.read_csv("data/destinations.csv")

# Load a pretrained embedding model
# This model turns any sentence into a 384-dimensional vector
model = SentenceTransformer('all-MiniLM-L6-v2')

# Combine description with a few key fields for richer context
# (This is a small trick: giving the model a bit more than just the raw description
# often improves how well it captures the "vibe")
def build_text(row):
    return (
        f"{row['name']}, {row['region_type']} destination in {row['state']}. "
        f"{row['description']} "
        f"Budget level: {row['budget_level']}. Crowd level: {row['crowd_level']}."
    )

df['text_for_embedding'] = df.apply(build_text, axis=1)

# Generate embeddings for all destinations at once
embeddings = model.encode(df['text_for_embedding'].tolist(), show_progress_bar=True)

# Save embeddings + the dataframe order so we can reload without recomputing
np.save("data/destination_embeddings.npy", embeddings)
df.to_csv("data/destinations_processed.csv", index=False)

print(f"Generated embeddings for {len(df)} destinations")
print(f"Embedding shape: {embeddings.shape}")
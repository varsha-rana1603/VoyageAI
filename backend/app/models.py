from sentence_transformers import SentenceTransformer # type: ignore

# Load a pretrained embedding model
# This model turns any sentence into a 384-dimensional vector
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
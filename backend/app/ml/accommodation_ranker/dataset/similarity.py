import numpy as np


def cosine_similarity(
    embedding1,
    embedding2,
) -> float:

    if embedding1 is None or embedding2 is None:
        return 0.0

    embedding1 = np.asarray(embedding1, dtype=float)
    embedding2 = np.asarray(embedding2, dtype=float)

    if embedding1.size == 0 or embedding2.size == 0:
        return 0.0

    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    similarity = np.dot(
        embedding1,
        embedding2,
    ) / (norm1 * norm2)

    return float(similarity)
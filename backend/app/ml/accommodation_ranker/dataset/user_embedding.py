from app.conversation.user_profile import UserProfile
from app.ml.embeddings import (
    embed_text,
    profile_to_embedding_text,
)


def generate_user_embedding(
    profile: UserProfile,
) -> list[float]:

    text = profile_to_embedding_text(
        profile,
    )

    return embed_text(text)
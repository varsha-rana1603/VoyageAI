#CREATES TRAINNING DATASET
"""
(UserProfile,
 Accommodation)
        │
        ▼
build_feature_vector()

        +
generate_target_score()

        ▼
TrainingExample
"""

from app.conversation.user_profile import UserProfile
from app.models.accommodation import Accommodation

from ..schemas import TrainingExample

from .features import build_feature_vector
from .labels import generate_target_score
from .user_embedding import generate_user_embedding


def generate_training_examples(
    profile: UserProfile,
    accommodations: list[Accommodation],
) -> list[TrainingExample]:

    examples = []

    user_embedding = generate_user_embedding(
        profile,
    )

    for hotel in accommodations:

        features = build_feature_vector(
            profile,
            hotel,
            user_embedding,
        )

        target = generate_target_score(
            profile,
            hotel,
        )

        examples.append(
            TrainingExample(
                feature_vector=features,
                target_score=target,
                accommodation_id=str(hotel.id),
                destination_id=str(
                    hotel.destination_id
                ),
            )
        )

    return examples
from pathlib import Path

from xgboost import XGBRegressor
import numpy as np
from sqlalchemy.orm import Session

from app.conversation.user_profile import UserProfile
from app.models.accommodation import Accommodation

from app.ml.accommodation_ranker.dataset.features import (
    build_feature_vector,
)
from app.ml.accommodation_ranker.dataset.user_embedding import (
    generate_user_embedding,
)
from app.ml.accommodation_ranker.explanations import (
    generate_accommodation_reasons,
)

from ..schemas import RankedAccommodation


MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "models"
    / "accommodation_ranker.json"
)


class AccommodationRanker:

    def __init__(self):

        self.model = XGBRegressor()
        self.model.load_model(MODEL_PATH)

    def rank(
        self,
        profile: UserProfile,
        accommodations: list[Accommodation],
        top_k: int = 10,
    ) -> list[RankedAccommodation]:

        if not accommodations:
            return []

        user_embedding = generate_user_embedding(
            profile,
        )

        feature_vectors = []

        for hotel in accommodations:

            vector = build_feature_vector(
                profile=profile,
                accommodation=hotel,
                user_embedding=user_embedding,
            )

            feature_vectors.append(
                vector.values
            )

        predictions = self.model.predict(
            np.asarray(feature_vectors)
        )

        ranked = [
            RankedAccommodation(
                accommodation=hotel,
                score=float(score),
                reasons=generate_accommodation_reasons(profile, hotel)
            )
            for hotel, score in zip(
                accommodations,
                predictions,
            )

        ]

        ranked.sort(
            key=lambda x: x.score,
            reverse=True,
        )

        return ranked[:top_k]


# Singleton
ranker = AccommodationRanker()


def recommend_accommodations(
    db: Session,
    destination_id,
    profile: UserProfile,
    top_k: int = 10,
) -> list[RankedAccommodation]:

    hotels = (

        db.query(Accommodation)

        .filter(
            Accommodation.destination_id
            == destination_id
        )

        .all()

    )

    if not hotels:
        return []

    return ranker.rank(
        profile=profile,
        accommodations=hotels,
        top_k=top_k,
    )
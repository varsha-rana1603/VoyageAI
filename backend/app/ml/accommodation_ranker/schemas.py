from dataclasses import dataclass
from app.models.accommodation import Accommodation


@dataclass(slots=True)
class FeatureVector:
    # Numerical features representing one (user, accommodation) pair.
    values: list[float]

    @property
    def dimension(self) -> int:
        return len(self.values)


@dataclass(slots=True)
class TrainingExample:
    # One supervised learning example.
    feature_vector: FeatureVector
    target_score: float
    accommodation_id: str
    destination_id: str

@dataclass(slots=True)
class RankedAccommodation:

    accommodation: Accommodation
    score: float
    reasons: list[str]
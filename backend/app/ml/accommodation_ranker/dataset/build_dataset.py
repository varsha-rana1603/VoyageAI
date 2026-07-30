"""
Load all accommodations and generate a training dataset.
"""

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.conversation.user_profile import UserProfile
from app.models.accommodation import Accommodation

from .generator import generate_training_examples
from .export import export_dataset
from .profile_generator import generate_random_profiles


def build_dataset(
    db: Session,
    user_profiles: list[UserProfile],
):

    hotels = (
        db.query(Accommodation)
        .all()
    )

    examples = []

    for profile in user_profiles:

        examples.extend(
            generate_training_examples(
                profile,
                hotels,
            )
        )

    return examples


def main():

    db = SessionLocal()

    try:

        print("Generating random profiles...")

        profiles = generate_random_profiles(
            500,
        )

        print(f"Generated {len(profiles)} profiles")

        print("Building training examples...")

        examples = build_dataset(
            db=db,
            user_profiles=profiles,
        )

        print(f"Generated {len(examples)} examples")

        export_dataset(
            examples=examples,
            output_path="training_dataset.csv",
        )

        print("Saved training_dataset.csv")

    finally:

        db.close()


if __name__ == "__main__":
    main()
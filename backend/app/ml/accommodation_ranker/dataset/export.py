import pandas as pd

from ..constants import FEATURE_NAMES
from ..schemas import TrainingExample


def export_dataset(
    examples: list[TrainingExample],
    output_path: str,
):
    """
    Export training examples to CSV.
    """

    rows = []

    for example in examples:

        row = {
            name: value
            for name, value in zip(
                FEATURE_NAMES,
                example.feature_vector.values,
            )
        }

        row["target"] = example.target_score
        row["hotel_id"] = example.accommodation_id
        row["destination_id"] = example.destination_id

        rows.append(row)

    df = pd.DataFrame(rows)

    df.to_csv(
        output_path,
        index=False,
    )

    return df

if __name__ == "__main__":
    export_dataset()
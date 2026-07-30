from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from sklearn.model_selection import train_test_split

from app.ml.accommodation_ranker.constants import FEATURE_NAMES


MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "models"
    / "accommodation_ranker.joblib"
)


def evaluate(
    dataset_path: str,
):

    df = pd.read_csv(dataset_path)

    X = df[FEATURE_NAMES]
    y = df["target"]

    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    model = joblib.load(
        MODEL_PATH,
    )

    predictions = model.predict(
        X_test,
    )

    print("=" * 80)
    print("Evaluation Metrics")
    print("=" * 80)

    print(
        f"MAE  : {mean_absolute_error(y_test, predictions):.4f}"
    )

    print(
        f"RMSE : {(mean_squared_error(y_test, predictions) ** 0.5):.4f}"
    )

    print(
        f"R²   : {r2_score(y_test, predictions):.4f}"
    )

    print()

    print("=" * 80)
    print("Top Feature Importances")
    print("=" * 80)

    importance = sorted(
        zip(
            FEATURE_NAMES,
            model.feature_importances_,
        ),
        key=lambda x: x[1],
        reverse=True,
    )

    for feature, score in importance:
        print(
            f"{feature:<35} {score:.4f}"
        )

    print()

    print("=" * 80)
    print("Prediction Samples")
    print("=" * 80)

    for truth, pred in list(
        zip(
            y_test,
            predictions,
        )
    )[:10]:

        print(
            f"Actual: {truth:.3f}   Predicted: {pred:.3f}"
        )


if __name__ == "__main__":

    evaluate(
        "training_dataset.csv",
    )
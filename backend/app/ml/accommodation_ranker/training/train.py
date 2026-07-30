from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (mean_absolute_error, mean_squared_error,r2_score)
from xgboost import XGBRegressor

from app.ml.accommodation_ranker.constants import FEATURE_NAMES

MODEL_PATH = (
    Path(__file__).resolve().parents[1] / "models" / "accommodation_ranker.json"
    )

def train(dataset_path: str):
    df = pd.read_csv(dataset_path)
    X = df[FEATURE_NAMES]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    print("=" * 80)
    print("Training Results")
    print("=" * 80)
    print(f"MAE : {mean_absolute_error(y_test, predictions):.4f}")
    print(f"RMSE : {mean_squared_error(y_test, predictions) ** 0.5:.4f}")
    print(f"R² : {r2_score(y_test, predictions):.4f}")

    MODEL_PATH.parent.mkdir(parents = True, exist_ok = True)
    model.save_model(MODEL_PATH)
    print()
    print(f"Saved model to {MODEL_PATH}")
    return model

if __name__ == "__main__":
    train("training_dataset.csv")
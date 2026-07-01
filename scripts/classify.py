from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

def main():
    df = pd.read_csv(DATA_DIR / "features.csv")

    feature_cols = ["ndvi", "ndwi", "vv", "vh"]
    X = df[feature_cols]
    y = df["class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y if len(y.unique()) > 1 else None
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print("Accuracy:", acc)

    joblib.dump(model, DATA_DIR / "crop_model.joblib")
    df["pred_class"] = model.predict(X)
    df.to_csv(DATA_DIR / "classified_points.csv", index=False)
    print("Saved model and classified points.")

if __name__ == "__main__":
    main()
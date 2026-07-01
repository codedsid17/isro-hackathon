from pathlib import Path
import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

def load_inputs():
    roi = gpd.read_file(DATA_DIR / "roi.geojson")
    points = gpd.read_file(DATA_DIR / "training_points.geojson")
    return roi, points

def build_features(points_gdf):
    df = pd.DataFrame(points_gdf.drop(columns="geometry"))
    n = len(df)

    if "ndvi" not in df.columns:
        df["ndvi"] = np.linspace(0.30, 0.65, n)
    if "ndwi" not in df.columns:
        df["ndwi"] = np.linspace(0.12, 0.03, n)
    if "vv" not in df.columns:
        df["vv"] = np.linspace(-11.5, -10.0, n)
    if "vh" not in df.columns:
        df["vh"] = np.linspace(-16.8, -14.8, n)
    if "rainfall" not in df.columns:
        df["rainfall"] = np.linspace(0, 15, n)

    return df

def train_model(df):
    feature_cols = ["ndvi", "ndwi", "vv", "vh", "rainfall"]
    X = df[feature_cols]
    y = df["class"]

    stratify = y if y.nunique() > 1 and y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=stratify
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    return model, acc, feature_cols

def add_stress_advisory(df):
    def stress_level(row):
        if row["ndvi"] < 0.40 or row["ndwi"] < 0.05:
            return "high"
        elif row["ndvi"] < 0.55:
            return "moderate"
        return "low"

    def advisory(stress):
        if stress == "high":
            return "irrigate_now"
        elif stress == "moderate":
            return "monitor"
        return "no_irrigation"

    df["stress"] = df.apply(stress_level, axis=1)
    df["advisory"] = df["stress"].apply(advisory)
    return df

def export_outputs(df, model, acc):
    model_path = DATA_DIR / "crop_model.joblib"
    joblib.dump(model, model_path)

    if "lon" not in df.columns:
        df["lon"] = 76.10 + (df.index * 0.01)
    if "lat" not in df.columns:
        df["lat"] = 18.50 + (df.index * 0.01)

    gdf = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df["lon"], df["lat"])],
        crs="EPSG:4326"
    )

    crop_out = gdf[["crop", "class", "pred_class", "geometry"]].copy()
    if "crop" not in crop_out.columns:
        crop_out["crop"] = crop_out["class"].astype(str)

    stress_out = gdf[["stress", "geometry"]].copy()

    crop_out.to_file(DATA_DIR / "crop_map.geojson", driver="GeoJSON")
    stress_out.to_file(DATA_DIR / "stress_map.geojson", driver="GeoJSON")

    adv = gdf[["field_id", "crop", "stress", "advisory"]].copy()
    if "field_id" not in adv.columns:
        adv["field_id"] = np.arange(1, len(adv) + 1)
    adv.to_csv(DATA_DIR / "advisory.csv", index=False)

    ts_cols = ["field_id", "crop", "ndvi", "ndwi", "vv", "vh", "rainfall", "stress", "advisory"]
    if "field_id" not in gdf.columns:
        gdf["field_id"] = np.arange(1, len(gdf) + 1)
    gdf[ts_cols].to_csv(DATA_DIR / "timeseries.csv", index=False)

    report = pd.DataFrame([{
        "accuracy": acc,
        "records": len(df)
    }])
    report.to_csv(DATA_DIR / "run_report.csv", index=False)

def main():
    _, points = load_inputs()
    df = build_features(points)
    model, acc, feature_cols = train_model(df)
    df["pred_class"] = model.predict(df[feature_cols])
    df = add_stress_advisory(df)
    export_outputs(df, model, acc)
    print("Pipeline complete.")
    print("Accuracy:", acc)

if __name__ == "__main__":
    main()
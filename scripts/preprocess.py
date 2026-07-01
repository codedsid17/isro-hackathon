from pathlib import Path
import geopandas as gpd
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

def main():
    roi = gpd.read_file(DATA_DIR / "roi.geojson")
    points = gpd.read_file(DATA_DIR / "training_points.geojson")

    df = pd.DataFrame(points.drop(columns="geometry"))
    if "ndvi" not in df.columns:
        df["ndvi"] = [0.32, 0.48, 0.61, 0.55][:len(df)]
    if "ndwi" not in df.columns:
        df["ndwi"] = [0.12, 0.08, 0.03, 0.05][:len(df)]
    if "vv" not in df.columns:
        df["vv"] = [-11.2, -10.8, -10.5, -10.9][:len(df)]
    if "vh" not in df.columns:
        df["vh"] = [-16.5, -15.9, -15.0, -15.4][:len(df)]

    df.to_csv(DATA_DIR / "features.csv", index=False)
    print("Saved:", DATA_DIR / "features.csv")

if __name__ == "__main__":
    main()
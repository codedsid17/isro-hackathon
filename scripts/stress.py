from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

def main():
    df = pd.read_csv(DATA_DIR / "classified_points.csv")

    def stress_level(row):
        if row["ndvi"] < 0.4 or row["ndwi"] < 0.05:
            return "high"
        elif row["ndvi"] < 0.55:
            return "moderate"
        return "low"

    df["stress"] = df.apply(stress_level, axis=1)
    df.to_csv(DATA_DIR / "stress_points.csv", index=False)
    print("Saved:", DATA_DIR / "stress_points.csv")

if __name__ == "__main__":
    main()
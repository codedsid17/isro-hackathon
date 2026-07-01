from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

def map_advisory(stress):
    if stress == "high":
        return "irrigate_now"
    if stress == "moderate":
        return "monitor"
    return "no_irrigation"

def main():
    df = pd.read_csv(DATA_DIR / "stress_points.csv")
    df["advisory"] = df["stress"].apply(map_advisory)
    df.to_csv(DATA_DIR / "advisory.csv", index=False)
    print("Saved:", DATA_DIR / "advisory.csv")

if __name__ == "__main__":
    main()
from flask import Flask, render_template, jsonify, send_from_directory
import pandas as pd
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/data/<path:filename>")
def data_files(filename):
    return send_from_directory(DATA_DIR, filename)

@app.route("/api/advisory")
def advisory_api():
    path = DATA_DIR / "advisory.csv"
    if path.exists():
        df = pd.read_csv(path)
        return df.to_json(orient="records")
    return jsonify([])

@app.route("/api/timeseries")
def timeseries_api():
    path = DATA_DIR / "timeseries.csv"
    if path.exists():
        df = pd.read_csv(path)
        return df.to_json(orient="records")
    return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)
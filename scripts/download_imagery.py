from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

def main():
    print("Download step placeholder.")
    print("Put raw satellite files here if you have them:", DATA_DIR)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Download and clean the UCI processed Cleveland dataset."""

from pathlib import Path

from heart_disease_mlops.data import (
    clean_heart_data,
    download_raw_data,
    load_raw_data,
    save_clean_data,
)


def main() -> None:
    raw_path = Path("data/raw/processed.cleveland.data")
    clean_path = Path("data/processed/heart_disease_clean.csv")
    download_raw_data(raw_path)
    frame = clean_heart_data(load_raw_data(raw_path))
    save_clean_data(frame, clean_path)
    print(f"Saved {len(frame)} cleaned rows to {clean_path}")


if __name__ == "__main__":
    main()


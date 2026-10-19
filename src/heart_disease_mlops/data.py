"""Data acquisition, validation, cleaning, and preprocessing."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "heart-disease/processed.cleveland.data"
)

RAW_COLUMNS = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "target",
]

FEATURE_COLUMNS = RAW_COLUMNS[:-1]
NUMERIC_FEATURES = ["age", "trestbps", "chol", "thalach", "oldpeak"]
CATEGORICAL_FEATURES = [
    "sex",
    "cp",
    "fbs",
    "restecg",
    "exang",
    "slope",
    "ca",
    "thal",
]


def download_raw_data(output_path: Path, url: str = DATA_URL) -> Path:
    """Download the UCI processed Cleveland dataset."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "heart-disease-mlops/0.1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
    if len(payload) < 1_000:
        raise ValueError("Downloaded dataset is unexpectedly small")
    output_path.write_bytes(payload)
    return output_path


def load_raw_data(path: Path) -> pd.DataFrame:
    """Load the headerless raw UCI CSV."""
    return pd.read_csv(path, names=RAW_COLUMNS, na_values="?")


def clean_heart_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize types, target encoding, duplicates, and impossible values."""
    if list(frame.columns) != RAW_COLUMNS:
        if frame.shape[1] != len(RAW_COLUMNS):
            raise ValueError(f"Expected {len(RAW_COLUMNS)} columns, found {frame.shape[1]}")
        frame = frame.copy()
        frame.columns = RAW_COLUMNS
    else:
        frame = frame.copy()

    frame = frame.replace("?", np.nan)
    for column in RAW_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    frame = frame.dropna(subset=["target"])
    frame["target"] = (frame["target"] > 0).astype(int)
    frame = frame.drop_duplicates().reset_index(drop=True)

    invalid_age = frame["age"].notna() & ~frame["age"].between(18, 100)
    invalid_cholesterol = frame["chol"].notna() & (frame["chol"] <= 0)
    if invalid_age.any() or invalid_cholesterol.any():
        raise ValueError("Dataset contains impossible age or cholesterol values")
    return frame


def save_clean_data(frame: pd.DataFrame, output_path: Path) -> Path:
    """Save cleaned data and a compact data-quality profile."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    profile = {
        "rows": int(len(frame)),
        "columns": list(frame.columns),
        "duplicate_rows": int(frame.duplicated().sum()),
        "missing_values": {key: int(value) for key, value in frame.isna().sum().items()},
        "target_distribution": {
            str(key): int(value) for key, value in frame["target"].value_counts().items()
        },
    }
    output_path.with_suffix(".profile.json").write_text(
        json.dumps(profile, indent=2), encoding="utf-8"
    )
    return output_path


def load_clean_data(path: Path) -> pd.DataFrame:
    """Load and validate a cleaned dataset."""
    frame = pd.read_csv(path)
    missing_columns = set(RAW_COLUMNS) - set(frame.columns)
    if missing_columns:
        raise ValueError(f"Clean dataset is missing columns: {sorted(missing_columns)}")
    if not set(frame["target"].unique()).issubset({0, 1}):
        raise ValueError("Target must be binary")
    return frame[RAW_COLUMNS]


def build_preprocessor() -> ColumnTransformer:
    """Build the reusable preprocessing transformer."""
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )


def split_features_target(
    frame: pd.DataFrame, test_size: float = 0.2, random_state: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Create a reproducible stratified holdout split."""
    features = frame[FEATURE_COLUMNS]
    target = frame["target"]
    return train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=random_state,
        stratify=target,
    )


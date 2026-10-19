#!/usr/bin/env python3
"""Run one local prediction from a JSON request file."""

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

from heart_disease_mlops.data import FEATURE_COLUMNS


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("examples/sample_request.json"))
    parser.add_argument("--model", type=Path, default=Path("models/heart_disease_pipeline.joblib"))
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    frame = pd.DataFrame([payload])[FEATURE_COLUMNS]
    model = joblib.load(args.model)
    prediction = int(model.predict(frame)[0])
    probability = float(model.predict_proba(frame)[0, 1])
    print(
        json.dumps(
            {
                "prediction": prediction,
                "risk_label": "higher_risk" if prediction else "lower_risk",
                "positive_class_probability": round(probability, 6),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()


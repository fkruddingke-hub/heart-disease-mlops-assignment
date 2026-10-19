import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression

from heart_disease_mlops.data import FEATURE_COLUMNS
from heart_disease_mlops.train import build_pipeline


@pytest.fixture
def trained_pipeline():
    rows = [
        [35, 0, 2, 118, 180, 0, 0, 175, 0, 0.0, 1, 0, 3],
        [40, 1, 2, 125, 210, 0, 0, 168, 0, 0.5, 1, 0, 3],
        [48, 0, 3, 130, 225, 0, 1, 158, 0, 0.8, 2, 0, 3],
        [52, 1, 4, 140, 260, 1, 1, 135, 1, 2.0, 2, 1, 7],
        [60, 1, 4, 150, 290, 0, 2, 120, 1, 3.0, 3, 2, 7],
        [67, 0, 4, 160, 310, 1, 2, 110, 1, 4.0, 3, 3, 7],
    ]
    features = pd.DataFrame(rows, columns=FEATURE_COLUMNS)
    target = pd.Series([0, 0, 0, 1, 1, 1])
    pipeline = build_pipeline(LogisticRegression(max_iter=1_000, random_state=42))
    pipeline.fit(features, target)
    return pipeline


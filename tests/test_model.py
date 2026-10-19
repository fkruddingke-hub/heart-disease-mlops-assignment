import numpy as np
import pandas as pd

from heart_disease_mlops.data import FEATURE_COLUMNS


def test_pipeline_predicts_probabilities(trained_pipeline):
    features = pd.DataFrame(
        [[55, 1, 3, 135, 240, 0, 1, 145, 0, 1.2, 2, 1, 6]],
        columns=FEATURE_COLUMNS,
    )
    probabilities = trained_pipeline.predict_proba(features)
    assert probabilities.shape == (1, 2)
    assert np.isclose(probabilities.sum(), 1.0)

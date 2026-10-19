import numpy as np
import pandas as pd

from heart_disease_mlops.data import RAW_COLUMNS, clean_heart_data, split_features_target


def test_clean_data_converts_target_and_missing_values():
    raw = pd.DataFrame(
        [
            [63, 1, 1, 145, 233, 1, 2, 150, 0, 2.3, 3, "?", 6, 0],
            [67, 1, 4, 160, 286, 0, 2, 108, 1, 1.5, 2, 3, 3, 2],
        ],
        columns=RAW_COLUMNS,
    )
    cleaned = clean_heart_data(raw)
    assert cleaned["target"].tolist() == [0, 1]
    assert np.isnan(cleaned.loc[0, "ca"])


def test_split_is_stratified():
    rows = []
    for index in range(20):
        rows.append([50 + index, 1, 3, 120, 200, 0, 0, 150, 0, 1.0, 2, 0, 3, index % 2])
    frame = pd.DataFrame(rows, columns=RAW_COLUMNS)
    _, _, target_train, target_test = split_features_target(frame, test_size=0.2)
    assert target_train.mean() == 0.5
    assert target_test.mean() == 0.5


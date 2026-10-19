#!/usr/bin/env python3
"""Generate reproducible EDA tables and professional visualizations."""

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

from heart_disease_mlops.data import load_clean_data


def main() -> None:
    data_path = Path("data/processed/heart_disease_clean.csv")
    output_dir = Path("outputs/eda")
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = load_clean_data(data_path)

    frame.describe(include="all").transpose().to_csv(output_dir / "descriptive_statistics.csv")
    pd.DataFrame(
        {
            "column": frame.columns,
            "dtype": [str(dtype) for dtype in frame.dtypes],
            "missing_count": frame.isna().sum().values,
            "missing_percent": (frame.isna().mean().values * 100).round(2),
            "unique_values": frame.nunique(dropna=True).values,
        }
    ).to_csv(output_dir / "data_quality.csv", index=False)

    sns.set_theme(style="whitegrid", context="notebook")

    figure, axes = plt.subplots(2, 2, figsize=(12, 8))
    for axis, column in zip(axes.flat, ["age", "trestbps", "chol", "thalach"]):
        sns.histplot(data=frame, x=column, hue="target", kde=True, ax=axis, element="step")
        axis.set_title(f"{column} by target")
    figure.suptitle("Heart Disease Feature Distributions", fontsize=16)
    figure.tight_layout()
    figure.savefig(output_dir / "feature_histograms.png", dpi=180)
    plt.close(figure)

    plt.figure(figsize=(12, 9))
    sns.heatmap(frame.corr(numeric_only=True), cmap="vlag", center=0, square=True)
    plt.title("Feature Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(output_dir / "correlation_heatmap.png", dpi=180)
    plt.close()

    counts = frame["target"].value_counts().sort_index()
    plt.figure(figsize=(7, 5))
    axis = sns.barplot(x=["No disease", "Disease"], y=counts.values, hue=counts.index, legend=False)
    axis.bar_label(axis.containers[0])
    plt.ylabel("Patient records")
    plt.title("Target Class Balance")
    plt.tight_layout()
    plt.savefig(output_dir / "class_balance.png", dpi=180)
    plt.close()

    print(f"EDA artifacts written to {output_dir}")


if __name__ == "__main__":
    main()


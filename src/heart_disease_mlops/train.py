"""Train, compare, track, and package heart-disease classifiers."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import joblib
import matplotlib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline

from heart_disease_mlops.data import (
    FEATURE_COLUMNS,
    build_preprocessor,
    load_clean_data,
    split_features_target,
)

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RANDOM_STATE = 42


def candidate_models() -> list[tuple[str, Any, dict[str, Any]]]:
    """Return personalized model candidates and tuning settings."""
    return [
        (
            "logistic_c_0_1",
            LogisticRegression(C=0.1, max_iter=2_000, random_state=RANDOM_STATE),
            {"model_family": "logistic_regression", "C": 0.1},
        ),
        (
            "logistic_c_1",
            LogisticRegression(C=1.0, max_iter=2_000, random_state=RANDOM_STATE),
            {"model_family": "logistic_regression", "C": 1.0},
        ),
        (
            "logistic_c_10",
            LogisticRegression(C=10.0, max_iter=2_000, random_state=RANDOM_STATE),
            {"model_family": "logistic_regression", "C": 10.0},
        ),
        (
            "random_forest_depth_5",
            RandomForestClassifier(
                n_estimators=300,
                max_depth=5,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=1,
            ),
            {"model_family": "random_forest", "n_estimators": 300, "max_depth": 5},
        ),
        (
            "random_forest_unbounded",
            RandomForestClassifier(
                n_estimators=300,
                max_depth=None,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=1,
            ),
            {"model_family": "random_forest", "n_estimators": 300, "max_depth": "none"},
        ),
    ]


def build_pipeline(estimator: Any) -> Pipeline:
    """Join preprocessing and classification into one deployable object."""
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("classifier", estimator),
        ]
    )


def evaluate_pipeline(
    pipeline: Pipeline,
    features_train: pd.DataFrame,
    target_train: pd.Series,
    features_test: pd.DataFrame,
    target_test: pd.Series,
) -> tuple[dict[str, float], np.ndarray, np.ndarray]:
    """Run five-fold CV, fit, and evaluate the holdout data."""
    cross_validation = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scoring = ["accuracy", "precision", "recall", "roc_auc"]
    cv_results = cross_validate(
        pipeline,
        features_train,
        target_train,
        cv=cross_validation,
        scoring=scoring,
        n_jobs=1,
    )
    pipeline.fit(features_train, target_train)
    predictions = pipeline.predict(features_test)
    probabilities = pipeline.predict_proba(features_test)[:, 1]
    metrics = {
        "cv_accuracy_mean": float(cv_results["test_accuracy"].mean()),
        "cv_precision_mean": float(cv_results["test_precision"].mean()),
        "cv_recall_mean": float(cv_results["test_recall"].mean()),
        "cv_roc_auc_mean": float(cv_results["test_roc_auc"].mean()),
        "cv_roc_auc_std": float(cv_results["test_roc_auc"].std()),
        "test_accuracy": float(accuracy_score(target_test, predictions)),
        "test_precision": float(precision_score(target_test, predictions, zero_division=0)),
        "test_recall": float(recall_score(target_test, predictions, zero_division=0)),
        "test_roc_auc": float(roc_auc_score(target_test, probabilities)),
    }
    return metrics, predictions, probabilities


def save_evaluation_plots(
    target_test: pd.Series,
    predictions: np.ndarray,
    probabilities: np.ndarray,
    destination: Path,
    candidate_name: str,
) -> list[Path]:
    """Save confusion-matrix and ROC artifacts for one run."""
    destination.mkdir(parents=True, exist_ok=True)
    confusion_path = destination / f"{candidate_name}_confusion_matrix.png"
    roc_path = destination / f"{candidate_name}_roc_curve.png"

    ConfusionMatrixDisplay.from_predictions(target_test, predictions, cmap="Blues")
    plt.title(f"Confusion Matrix: {candidate_name}")
    plt.tight_layout()
    plt.savefig(confusion_path, dpi=160)
    plt.close()

    false_positive_rate, true_positive_rate, _ = roc_curve(target_test, probabilities)
    plt.figure(figsize=(6, 5))
    plt.plot(false_positive_rate, true_positive_rate, label=candidate_name)
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Holdout ROC Curve")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(roc_path, dpi=160)
    plt.close()
    return [confusion_path, roc_path]


def train_and_select(
    data_path: Path,
    model_path: Path,
    metadata_path: Path,
    output_dir: Path,
    mlflow_db: Path,
) -> dict[str, Any]:
    """Track all candidates and persist the best complete pipeline."""
    frame = load_clean_data(data_path)
    features_train, features_test, target_train, target_test = split_features_target(frame)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    mlflow_db.parent.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(f"sqlite:///{mlflow_db.resolve()}")
    mlflow.set_experiment("heart-disease-classification")

    leaderboard: list[dict[str, Any]] = []
    fitted_models: dict[str, Pipeline] = {}

    for candidate_name, estimator, parameters in candidate_models():
        pipeline = build_pipeline(estimator)
        with mlflow.start_run(run_name=candidate_name) as run:
            metrics, predictions, probabilities = evaluate_pipeline(
                pipeline,
                features_train,
                target_train,
                features_test,
                target_test,
            )
            mlflow.log_params(
                {
                    **parameters,
                    "random_state": RANDOM_STATE,
                    "test_size": 0.2,
                    "cv_folds": 5,
                    "dataset_rows": len(frame),
                }
            )
            mlflow.log_metrics(metrics)
            with tempfile.TemporaryDirectory() as temporary_directory:
                paths = save_evaluation_plots(
                    target_test,
                    predictions,
                    probabilities,
                    Path(temporary_directory),
                    candidate_name,
                )
                for artifact_path in paths:
                    mlflow.log_artifact(str(artifact_path), artifact_path="evaluation")
                mlflow.sklearn.log_model(
                    pipeline,
                    artifact_path="model",
                    input_example=features_test.iloc[:3],
                )
            record = {
                "candidate": candidate_name,
                "run_id": run.info.run_id,
                **parameters,
                **metrics,
            }
            leaderboard.append(record)
            fitted_models[candidate_name] = pipeline

    leaderboard.sort(key=lambda record: record["test_roc_auc"], reverse=True)
    best_record = leaderboard[0]
    best_pipeline = fitted_models[best_record["candidate"]]
    joblib.dump(best_pipeline, model_path)

    leaderboard_path = output_dir / "model_leaderboard.csv"
    pd.DataFrame(leaderboard).to_csv(leaderboard_path, index=False)
    metadata = {
        "project": "heart-disease-mlops",
        "model_version": "1.0.0",
        "selection_metric": "test_roc_auc",
        "selected_candidate": best_record["candidate"],
        "selected_run_id": best_record["run_id"],
        "metrics": {
            key: value
            for key, value in best_record.items()
            if key.startswith("cv_") or key.startswith("test_")
        },
        "feature_order": FEATURE_COLUMNS,
        "dataset_rows": len(frame),
        "train_rows": len(features_train),
        "test_rows": len(features_test),
        "random_state": RANDOM_STATE,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (output_dir / "training_summary.json").write_text(
        json.dumps({"best_model": metadata, "leaderboard": leaderboard}, indent=2),
        encoding="utf-8",
    )

    best_predictions = best_pipeline.predict(features_test)
    best_probabilities = best_pipeline.predict_proba(features_test)[:, 1]
    save_evaluation_plots(
        target_test,
        best_predictions,
        best_probabilities,
        output_dir,
        "selected_model",
    )
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/processed/heart_disease_clean.csv"))
    parser.add_argument("--model", type=Path, default=Path("models/heart_disease_pipeline.joblib"))
    parser.add_argument("--metadata", type=Path, default=Path("models/model_metadata.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/modeling"))
    parser.add_argument("--mlflow-db", type=Path, default=Path("mlflow.db"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = train_and_select(
        data_path=args.data,
        model_path=args.model,
        metadata_path=args.metadata,
        output_dir=args.output_dir,
        mlflow_db=args.mlflow_db,
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()


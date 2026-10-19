"""FastAPI application for heart-disease risk prediction."""

from __future__ import annotations

import json
import logging
import os
import time
from functools import lru_cache
from pathlib import Path
from typing import Annotated

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

from heart_disease_mlops.data import FEATURE_COLUMNS

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
LOGGER = logging.getLogger("heart-disease-api")

REQUEST_COUNT = Counter(
    "heart_api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "heart_api_request_duration_seconds",
    "API request latency",
    ["method", "endpoint"],
)
PREDICTION_COUNT = Counter(
    "heart_api_predictions_total",
    "Predictions by returned class",
    ["prediction"],
)

MODEL_PATH = Path(os.getenv("MODEL_PATH", "models/heart_disease_pipeline.joblib"))
METADATA_PATH = Path(os.getenv("MODEL_METADATA_PATH", "models/model_metadata.json"))


class HeartDiseaseInput(BaseModel):
    """Validated UCI feature payload."""

    age: Annotated[float, Field(ge=18, le=100)]
    sex: Annotated[int, Field(ge=0, le=1)]
    cp: Annotated[int, Field(ge=1, le=4)]
    trestbps: Annotated[float, Field(gt=0, le=300)]
    chol: Annotated[float, Field(gt=0, le=800)]
    fbs: Annotated[int, Field(ge=0, le=1)]
    restecg: Annotated[int, Field(ge=0, le=2)]
    thalach: Annotated[float, Field(gt=0, le=250)]
    exang: Annotated[int, Field(ge=0, le=1)]
    oldpeak: Annotated[float, Field(ge=0, le=10)]
    slope: Annotated[int, Field(ge=1, le=3)]
    ca: Annotated[float, Field(ge=0, le=4)]
    thal: Annotated[float, Field(ge=3, le=7)]


class PredictionResponse(BaseModel):
    prediction: int
    risk_label: str
    confidence: float
    positive_class_probability: float
    model_version: str


@lru_cache(maxsize=1)
def get_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


@lru_cache(maxsize=1)
def get_metadata() -> dict:
    if not METADATA_PATH.exists():
        return {"model_version": "unknown"}
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


app = FastAPI(
    title="Heart Disease Risk API",
    description="Predicts heart-disease risk using a tracked UCI classifier.",
    version="1.0.0",
)


@app.middleware("http")
async def observe_request(request: Request, call_next):
    started = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        endpoint = request.url.path
        duration = time.perf_counter() - started
        REQUEST_COUNT.labels(request.method, endpoint, str(status_code)).inc()
        REQUEST_LATENCY.labels(request.method, endpoint).observe(duration)
        LOGGER.info(
            "request method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            endpoint,
            status_code,
            duration * 1_000,
        )


@app.get("/health")
def health() -> dict[str, str]:
    try:
        get_model()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"status": "ready", "model_version": get_metadata().get("model_version", "unknown")}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: HeartDiseaseInput) -> PredictionResponse:
    try:
        model = get_model()
        frame = pd.DataFrame([payload.model_dump()])[FEATURE_COLUMNS]
        prediction = int(model.predict(frame)[0])
        positive_probability = float(model.predict_proba(frame)[0, 1])
    except Exception as exc:
        LOGGER.exception("prediction_failed")
        raise HTTPException(status_code=500, detail="Prediction failed") from exc

    PREDICTION_COUNT.labels(str(prediction)).inc()
    confidence = positive_probability if prediction == 1 else 1.0 - positive_probability
    return PredictionResponse(
        prediction=prediction,
        risk_label="higher_risk" if prediction == 1 else "lower_risk",
        confidence=round(confidence, 6),
        positive_class_probability=round(positive_probability, 6),
        model_version=get_metadata().get("model_version", "unknown"),
    )


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


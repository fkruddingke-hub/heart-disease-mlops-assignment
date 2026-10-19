from fastapi.testclient import TestClient

from heart_disease_mlops import api


def test_predict_endpoint(monkeypatch, trained_pipeline):
    monkeypatch.setattr(api, "get_model", lambda: trained_pipeline)
    monkeypatch.setattr(api, "get_metadata", lambda: {"model_version": "test"})
    client = TestClient(api.app)
    response = client.post(
        "/predict",
        json={
            "age": 57,
            "sex": 1,
            "cp": 3,
            "trestbps": 130,
            "chol": 236,
            "fbs": 0,
            "restecg": 0,
            "thalach": 174,
            "exang": 0,
            "oldpeak": 0.0,
            "slope": 1,
            "ca": 1,
            "thal": 3,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["prediction"] in (0, 1)
    assert 0 <= body["confidence"] <= 1
    assert body["model_version"] == "test"


def test_invalid_payload_is_rejected():
    client = TestClient(api.app)
    response = client.post("/predict", json={"age": -1})
    assert response.status_code == 422


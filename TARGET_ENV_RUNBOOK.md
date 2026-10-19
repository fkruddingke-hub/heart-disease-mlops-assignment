# Target Environment Execution Runbook

This source package was intentionally not executed on the artifact-generation
machine. Run the following sequence on the destination machine and retain real
evidence from that environment.

## 1. Unpack and enter the project

```bash
unzip heart-disease-mlops-assignment.zip
cd heart-disease-mlops-assignment
```

Recommended baseline: Linux, Python 3.11, Git, Docker Engine with Compose,
`kubectl`, and Minikube.

## 2. Create the Python environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install --no-deps -e .
```

## 3. Run static checks and unit tests

```bash
mkdir -p outputs
python -m ruff check .
python -m pytest --junitxml=outputs/test-results.xml
```

Do not continue if either command fails.

## 4. Acquire and analyze the data

```bash
python scripts/download_data.py
MPLCONFIGDIR=/tmp/heart-disease-matplotlib python scripts/run_eda.py
```

Verify:

```bash
ls -lh data/raw/processed.cleveland.data
ls -lh data/processed/heart_disease_clean.csv
ls -lh outputs/eda
```

## 5. Train and track all candidates

```bash
MPLCONFIGDIR=/tmp/heart-disease-matplotlib \
  python -m heart_disease_mlops.train
```

Verify:

```bash
ls -lh models/heart_disease_pipeline.joblib
cat models/model_metadata.json
column -s, -t < outputs/modeling/model_leaderboard.csv
```

## 6. Review MLflow

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db \
  --host 127.0.0.1 --port 5000
```

Open `http://127.0.0.1:5000`, confirm five candidate runs, and capture
`02_mlflow_experiments.png` plus `03_mlflow_best_run.png`.

## 7. Test local inference and API serving

```bash
python scripts/predict.py --input examples/sample_request.json
uvicorn heart_disease_mlops.api:app --host 0.0.0.0 --port 8000
```

From another terminal:

```bash
cd heart-disease-mlops-assignment
curl --fail http://127.0.0.1:8000/health
curl --fail -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  --data @examples/sample_request.json
```

## 8. Build and smoke-test Docker

```bash
docker build -t heart-disease-api:1.0.0 .
docker run --rm --name heart-disease-api -p 8000:8000 \
  heart-disease-api:1.0.0
```

Repeat the health and prediction requests. Capture `04_docker_api.png` only
after both succeed.

## 9. Start monitoring

```bash
docker compose up --build -d
for request_number in $(seq 1 20); do
  curl --silent -X POST http://127.0.0.1:8000/predict \
    -H 'Content-Type: application/json' \
    --data @examples/sample_request.json >/dev/null
done
docker compose logs --tail=100 api
```

Verify Prometheus at `http://127.0.0.1:9090/targets` and Grafana at
`http://127.0.0.1:3000`. Capture the required monitoring evidence, then stop:

```bash
docker compose down
```

## 10. Deploy to Minikube

Follow `deployment/README.md`. The required proof is two ready API replicas,
service, Ingress, HPA, and a successful prediction through the deployed service.

## 11. Generate the final report

Place all real PNG evidence in `screenshots/`, update student details and the
repository URL in `reports/Assignment_01_Report.md` and
`scripts/generate_report.py`, then run:

```bash
python scripts/generate_report.py
ls -lh reports/Assignment_01_Report.docx
```

Open the DOCX and verify page layout, metrics, images, student identity, and URL
before submission.

## 12. Publish and record

Push the completed project to the student's GitHub repository, rerun GitHub
Actions, capture `01_ci_success.png`, and follow `video/RECORDING_GUIDE.md` to
record the real end-to-end demonstration.


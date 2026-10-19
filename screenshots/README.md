# Required screenshot evidence

Do not add fabricated or unrelated screenshots. Each image must show the real
repository/workflow/deployment produced for this assignment and remain readable
when inserted into the report.

| Filename | Capture exactly this evidence |
|---|---|
| `01_ci_success.png` | GitHub Actions summary with lint, tests, training, Docker build, and smoke test green |
| `02_mlflow_experiments.png` | MLflow experiment table showing all five candidate runs and metrics |
| `03_mlflow_best_run.png` | Best run parameters, metrics, ROC plot, and model artifact |
| `04_docker_api.png` | Terminal showing image build, running container, `/health`, and `/predict` response |
| `05_k8s_pods.png` | `kubectl -n heart-disease get pods,service,ingress,hpa` with ready replicas |
| `06_k8s_api.png` | Port-forward or Ingress request and successful JSON prediction |
| `07_prometheus_targets.png` | Prometheus targets page with `heart-disease-api` in UP state |
| `08_grafana_dashboard.png` | Provisioned dashboard containing non-empty request and prediction panels |
| `09_api_docs.png` | FastAPI `/docs` page with `/health` and `/predict` contracts |
| `10_repository.png` | Published repository root with project files and README visible |

Capture after executing the relevant workflow. Keep secrets, tokens, internal
hostnames, unrelated browser tabs, and patient-identifying information out of
all images.


# Short pipeline video guide

Recommended duration: 5–7 minutes.

1. **Problem and architecture (30 seconds)**
   - State the prediction goal and educational/non-clinical limitation.
   - Show `diagrams/architecture.svg`.
2. **Data and EDA (45 seconds)**
   - Run or describe `scripts/download_data.py`.
   - Show class balance, feature histograms, and correlation heatmap.
3. **Modeling and MLflow (60 seconds)**
   - Explain preprocessing inside the model pipeline.
   - Show five candidate runs, metrics, plots, and selected model.
4. **Tests and CI/CD (45 seconds)**
   - Show the tests and a green GitHub Actions run.
   - Explain that CI also builds and smoke-tests the container.
5. **API and Docker (60 seconds)**
   - Show `/docs`, `/health`, and one `/predict` response.
   - Point out prediction, confidence, and model version.
6. **Kubernetes (60 seconds)**
   - Show ready replicas, service, Ingress, HPA, and a live request.
7. **Monitoring and logs (45 seconds)**
   - Send several requests, then show Prometheus UP and Grafana panels.
   - Show request logs without payload content.
8. **Conclusion (15 seconds)**
   - Summarize reproducibility and identify limitations/future validation.

Before recording, close unrelated windows and remove credentials. Record actual
execution; do not narrate unverified deployment or CI results as successful.


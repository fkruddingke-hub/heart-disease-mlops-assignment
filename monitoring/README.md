# Monitoring and logging

The API emits structured request lines to standard output and exposes native
Prometheus metrics for request count, latency, status, and prediction class.

Start the complete local stack after training the model:

```bash
docker compose up --build -d
curl -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  --data @examples/sample_request.json
```

Open:

- API documentation: `http://127.0.0.1:8000/docs`
- Prometheus targets: `http://127.0.0.1:9090/targets`
- Grafana: `http://127.0.0.1:3000` (`admin` / `admin` for local coursework only)

The provisioned Grafana dashboard is under **MLOps Assignment → Heart Disease
API**. Generate several prediction requests before capturing evidence so the
graphs contain real observations.

Inspect logs with:

```bash
docker compose logs --tail=100 api
```

Stop the stack with `docker compose down`.


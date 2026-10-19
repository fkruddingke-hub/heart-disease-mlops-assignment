PYTHON := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: setup data eda train test lint report run docker compose-up compose-down clean

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	$(PIP) install --no-deps -e .

data:
	$(PYTHON) scripts/download_data.py

eda:
	MPLCONFIGDIR=/tmp/heart-disease-matplotlib $(PYTHON) scripts/run_eda.py

train:
	MPLCONFIGDIR=/tmp/heart-disease-matplotlib $(PYTHON) -m heart_disease_mlops.train

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

report:
	$(PYTHON) scripts/generate_report.py

run:
	$(PYTHON) -m uvicorn heart_disease_mlops.api:app --host 0.0.0.0 --port 8000

docker:
	docker build -t heart-disease-api:1.0.0 .

compose-up:
	docker compose up --build -d

compose-down:
	docker compose down

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

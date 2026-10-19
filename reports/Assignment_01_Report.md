# Assignment 01 Report Source

## End-to-End Heart Disease MLOps System

Student: **[Enter student name]**  
Student ID: **[Enter student ID]**  
Repository URL: **[Enter published repository URL]**

This project implements an original, reproducible MLOps workflow for binary
heart-disease risk classification using the UCI processed Cleveland dataset.
The final DOCX is generated with:

```bash
python scripts/generate_report.py
```

The generator creates ten explicitly separated report sections and reads real
metrics from `models/model_metadata.json` and
`outputs/modeling/model_leaderboard.csv`. It also inserts real CI, Kubernetes,
and Grafana screenshots when the expected files exist.

## Report Contents

1. Title and assignment identity
2. Executive summary and architecture
3. Data acquisition and quality
4. Exploratory data analysis
5. Feature engineering and reproducibility
6. Model development and evaluation
7. Experiment tracking and packaging
8. Automated testing and CI/CD
9. API, container, and Kubernetes deployment
10. Monitoring, evidence, and conclusion

## Finalization Notes

- Replace all bracketed student and repository fields.
- Execute the pipeline before generating the final DOCX so it includes real metrics.
- Capture the evidence named in `screenshots/README.md`.
- Regenerate the DOCX after screenshots are added.
- Add the real public URL, or retain the documented Minikube access instructions.
- Do not claim CI, Docker, Kubernetes, or monitoring execution without matching evidence.


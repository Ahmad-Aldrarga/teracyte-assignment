# TeraCyte – DevOps & MLOps Take-Home Assignment

This repository contains my implementation of the five required
DevOps/MLOps assignment tasks.

The solution focuses on reproducibility, automated verification,
secure model handoff, cost optimization, and infrastructure validation.

## 1. Implemented Features

| Task | Implementation |
|---|---|
| 1. Containerization | Docker Compose with API, Celery, Analysis, PostgreSQL, MongoDB and Redis |
| 2. E2E Verification | Five-image experiment verification, databases, model SHA-256 and execution time |
| 3. Model Lifecycle | Training, evaluation, versioned publication, selection and CI |
| 4. Cloud Architecture | Azure architecture, cost optimization and portability |
| 5. Terraform | Azure Blob Storage, private containers, lifecycle policies and CI validation |

## 2. System Architecture

The system processes images through a sequential analysis pipeline:

    Camera Images
          |
          v
     Preprocessing
          |
          v
     Mock Inference
     + Model SHA-256
          |
          v
    PostgreSQL Results
    MongoDB Experiment Status

FastAPI exposes application endpoints.

Celery and Redis support background report tasks.

Data/ML trains and evaluates models separately from application
delivery. Validated artifacts are selected through configuration
and verified before Analysis consumes them.

## 3. Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Terraform (for infrastructure validation)
- Git

No Azure subscription is required for local testing.

## 4. Quick Start

All commands run from the repository root.

### Install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-local.txt
```

### Build the Docker image

```bash
docker build -t teracyte-app:local .
```

### Start the services

```bash
docker compose up -d --wait
```

### Run E2E verification

```bash
python tests/e2e_verify.py
```

The E2E test:
- Uses a unique experiment ID.
- Processes exactly five images.
- Verifies five PostgreSQL records.
- Verifies MongoDB COMPLETED status.
- Validates the model SHA-256 independently.
- Requires Analysis to finish within 180 seconds.
- Returns a nonzero exit code on verification failure.

### Run unit tests

```bash
python -m pytest -q tests/test_starter.py tests/test_aggregation.py tests/test_model_lifecycle.py
```

### Stop the services

```bash
docker compose down
```

## 5. Model Lifecycle

The model workflow is:

    Train
      |
      v
    Evaluate / Quality Gate
      |
      v
    Publish Versioned Artifact
      |
      v
    Select Model Version
      |
      v
    Validate Format and SHA-256
      |
      v
    Analysis Consumer

### Train a model

```bash
python -m examples.model_lifecycle.train --output-dir data/model-lifecycle
```

This creates:
- data/model-lifecycle/model.json
- data/model-lifecycle/evaluation.json

### Publish version v1

```bash
python -m scripts.publish_model --model-path data/model-lifecycle/model.json --version v1
```

Publication rejects:
- Invalid model formats.
- Models that fail the MSE quality threshold.
- Existing model versions that would be overwritten.

### Verify the selected model

```bash
python -m scripts.model_handoff
```

Model selection is configured in:

    config/selected_model.json

### Run Analysis with the selected model

```bash
docker compose run --rm -e MODEL_SELECTION_CONFIG=/app/config/selected_model.json analysis python -m scripts.run_local --experiment-id model-v1-demo
```

The pipeline records the selected model artifact SHA-256.

Important: image inference is a deterministic mock.
The toy linear regression model is validated independently,
not used to generate real image predictions.

## 6. Continuous Integration

Two separate GitHub Actions workflows are implemented.

### Core Dev CI

File: `.github/workflows/ci-core-dev.yml`

Checks:
- Python application tests.
- Docker image build.
- Full E2E verification.
- Terraform formatting and validation.

### Data ML CI

File: `.github/workflows/ci-data-ml.yml`

Checks:
- ML unit tests.
- Model consumer compatibility.
- Model training and evaluation.
- Versioned publication and quality gate.
- Selected model and SHA-256 verification.
- Model artifact upload.

Shared application/model code changes trigger both workflows.

No cloud infrastructure is deployed by CI.

## 7. Terraform Infrastructure

Terraform configuration is located under `infra/`.

The design includes:
- Azure Storage Account using Standard LRS.
- Private containers for raw images, masks and models.
- Raw images moved to Cool after 7 days.
- Raw images and masks deleted after 30 days.
- Models excluded from automatic lifecycle deletion.
- HTTPS, TLS 1.2 and Microsoft Entra ID authentication.

Validate without deploying:

```bash
terraform fmt -check -recursive infra/
terraform -chdir=infra init -backend=false
terraform -chdir=infra validate
```

See [Terraform documentation](infra/README.md).

## 8. Documentation

- [Architecture and cost decisions](ARCHITECTURE_AND_DECISIONS.md)
- [Verification evidence](EVIDENCE.md)
- [Local development guide](docs/local-development.md)
- [Model lifecycle example](examples/model_lifecycle/README.md)

The original assignment requirements are preserved under `tasks/`.

## 9. Security and Limitations

- Generated data and model artifacts are excluded from Git.
- Terraform state files and credentials are not committed.
- Docker Compose uses development credentials only.
- Local storage uses bind mounts rather than cloud object storage.
- Analysis is sequential and uses mock image inference.
- Terraform is validated but not applied to Azure.
- Cloud costs are estimates based on assignment assumptions.

Production improvements would include authentication,
workload identity, private networking, managed databases,
distributed orchestration, observability and failure recovery.

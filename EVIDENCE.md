
# Evidence – TeraCyte Assignment

## Task 1 – Containerization

### Build the application image

```bash
docker build -t teracyte-app:local .
```

### Start the services

```bash
docker compose up -d --wait
docker compose ps
```

### Run analysis

```bash
docker compose run --rm analysis
```

Expected result:
- Experiment ID: demo-docker
- Five images processed
- Status: COMPLETED

### Verify through the API

```bash
curl -fsS http://127.0.0.1:8000/experiments/demo-docker/results
```

Observed result: COMPLETED with five image results.

### Generate a report

```bash
curl -i -X POST http://127.0.0.1:8000/experiments/demo-docker/exports
docker compose logs --tail=20 worker
```

Observed result:
- HTTP 202 Accepted
- Celery task succeeded
- Report: data/objects/reports/demo-docker.json

### Stop services

```bash
docker compose down
```

## Task 1 - Failure Handling

Test: Run the Analysis container with an intentionally invalid MongoDB URL.

Command:

    docker compose run --rm --no-deps \
      -e 'MONGO_URL=mongodb://127.0.0.1:1/?serverSelectionTimeoutMS=2000' \
      analysis

Expected result:
- MongoDB connection fails.
- Analysis terminates with a non-zero exit code.

Actual result:
- Exception: pymongo.errors.ServerSelectionTimeoutError
- Exit code: 1
- Result: PASS

The test demonstrates that the Analysis runner reports a dependency failure rather than silently succeeding.

## Task 2 - End-to-End Verification

### Purpose

Verify that a fresh analysis experiment produces the expected
records in PostgreSQL and MongoDB, uses the expected model artifact,
and completes within the configured time limit.

### Positive Test

Command:

    python tests/e2e_verify.py
    echo "E2E exit code: $?"

Observed results:
- Unique experiment ID generated
- PostgreSQL: exactly 5 image records with expected IDs
- MongoDB: status COMPLETED, result_count 5
- Model SHA-256: independently calculated before analysis and verified
- Analysis duration: 7.87 seconds
- Exit code: 0
- Result: PASS

### Negative Test - Incorrect Model SHA-256

Command:

    E2E_EXPECTED_SHA256=0000000000000000000000000000000000000000000000000000000000000000 python tests/e2e_verify.py
    echo "E2E exit code: $?"

Observed results:
- PostgreSQL verification: PASS
- MongoDB verification: PASS
- SHA-256 mismatch detected for image-001
- Exit code: 1
- Result: PASS (expected verification failure)

### Timeout Handling

- Configured analysis timeout: 180 seconds
- Python subprocess timeout triggers container cleanup and failure
- Timeout failure path has not been exercised separately
- Database startup occurs before the analysis timer starts

### Implementation

File: tests/e2e_verify.py

Each run creates a unique experiment ID to prevent existing
database records from producing a false positive.

## Task 3 - Model Lifecycle and CI

### Training and Evaluation

Command:

    python -m examples.model_lifecycle.train --output-dir data/model-lifecycle

Observed results:
- Training rows: 128
- Test rows: 64
- Baseline MSE: 2.6468672472
- Model MSE: 0.000111415
- Quality threshold: MSE < 0.001
- Result: PASS

### Model Publication

Command:

    python -m scripts.publish_model \
      --model-path data/model-lifecycle/model.json \
      --version v1

Published files:
- data/models/v1/model.json
- data/models/v1/metadata.json

Model SHA-256:
40bfe02753cb2b202f626f9d672dc49be7f780d7b17542cb9b8986604d48b10f

### Rejection Tests

Manually verified:
- Invalid version rejected (exit code 1)
- Missing model rejected without publication
- Corrupt JSON rejected without publication
- High-MSE model rejected without publication
- Existing v1 cannot be overwritten
- Tampered model rejected due to SHA-256 mismatch

### Model Handoff

Configuration:
    config/selected_model.json

Selected version: v1

The Analysis runner successfully loaded the selected artifact
and validated its SHA-256 before processing five images.

Experiment: model-v1-test-2
Status: COMPLETED
PostgreSQL: 5 rows with the expected v1 SHA-256

The image inference remains a deterministic mock; the linear
regression model is used as a versioned artifact dependency.

### Dev CI - GitHub Actions

Workflow: .github/workflows/dev-ci.yml
Run ID: 40109981821
Result: SUCCESS

Checks:
- Python application tests
- Docker image build

### ML CI - GitHub Actions

Workflow: .github/workflows/ml-ci.yml
Run ID: 40112354181
Result: SUCCESS

Checks:
- ML unit tests
- Training and evaluation
- Model publication
- SHA-256 verification
- Artifact upload

Artifact: validated-model-v1

The artifact was downloaded from GitHub Actions and independently
verified against its published metadata.

### Reproducibility

The data/ directory is gitignored. Model artifacts are regenerated
during ML CI and are not required to be committed to Git.

Publishing a new model does not automatically change the
selected model configuration.

## Task 5 - Terraform Infrastructure

### Infrastructure

Terraform defines:
- Azure Resource Group
- Standard LRS Storage Account
- Private containers: raw-images, masks, models
- Raw images: Cool after 7 days, delete after 30 days
- Masks: delete after 30 days
- Models: excluded from automatic deletion
- HTTPS, TLS 1.2 and Microsoft Entra ID authentication

### Local Verification

Terraform version: 1.17.0
AzureRM Provider: 4.81.0

Commands:
    terraform fmt -check -recursive infra/
    terraform -chdir=infra init -backend=false
    terraform -chdir=infra validate

Result: PASS

### GitHub Actions Verification

Workflow: .github/workflows/dev-ci.yml
Run ID: 40118953447
Result: SUCCESS

Jobs:
- test-and-build: PASS
- Terraform Validation: PASS

Terraform CI checks:
- Formatting: PASS
- Initialization: PASS
- Validation: PASS

No terraform apply was executed.
No Azure resources were created.

### Security and Reproducibility

- Terraform state files are excluded from Git.
- Provider lock file is committed.
- No credentials are stored in the repository.
- Production deployment requires Azure RBAC and
  appropriate network restrictions.

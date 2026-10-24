
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

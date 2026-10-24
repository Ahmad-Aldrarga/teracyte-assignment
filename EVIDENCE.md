
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

# Local development

[Back to the assignment](../README.md)

## What is supplied

The starter contains working Python steps and a sequential runner. Compose currently starts PostgreSQL, MongoDB and Redis; adding application containers is a required task.

| Location | Purpose |
|---|---|
| services/api/ | FastAPI registration/results endpoints and a Celery report task |
| pipelines/steps/preprocess/ | Otsu-like image mask generation |
| pipelines/steps/ml_infer/ | Mock inference and model SHA-256 recording |
| pipelines/steps/db_update/ | PostgreSQL upserts and MongoDB completion |
| scripts/generate_mock_data.py | Five deterministic images and mock weights |
| scripts/run_local.py | Sequential pipeline execution |
| tests/ | Small starter tests |
| examples/model_lifecycle/ | Data/ML notebook and equivalent CPU training/evaluation CLI |

## Run the baseline

Requirements: Python 3.11+ and Docker with Compose. Run commands from the repository root.

~~~bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-local.txt
docker compose up -d --wait
python -m pytest -q
python -m scripts.run_local --experiment-id demo-local
~~~

On first use, the runner generates five 3072 × 2048 PNGs and a 50 MiB mock weight file under data/. The weights are deterministic bytes, not a valid ONNX model. Successful execution reports five written rows and COMPLETED status.

The host defaults are:

| Variable | Default |
|---|---|
| POSTGRES_URL | postgresql://starter:starter@localhost:15432/experiments |
| MONGO_URL | mongodb://localhost:27018 |
| CELERY_BROKER_URL | redis://localhost:16379/0 |
| CELERY_RESULT_BACKEND | redis://localhost:16379/1 |

These host addresses are not container-to-container addresses. When containerizing, use Compose service names and internal ports: postgres:5432, mongo:27017 and redis:6379.

## Inspect the results

~~~bash
docker compose exec -T postgres psql -U starter -d experiments -c "SELECT experiment_id, count(*) FROM image_metrics GROUP BY experiment_id;"
docker compose exec -T mongo mongosh --quiet experiments --eval 'db.experiments.findOne({_id:"demo-local"})'
~~~

Start the API in one terminal:

~~~bash
python -m uvicorn services.api.main:app --reload
~~~

Start the worker in another terminal:

~~~bash
python -m celery -A services.api.tasks.celery_app worker --loglevel=INFO
~~~

Then inspect results and request a report:

~~~bash
curl http://127.0.0.1:8000/experiments/demo-local/results
curl -X POST http://127.0.0.1:8000/experiments/demo-local/exports
~~~

The worker writes data/objects/reports/demo-local.json. The API also accepts POST /experiments with an image_ids list. Registration alone does not launch analysis; the local runner registers experiments directly in MongoDB.

## Data contract

- Expected image IDs: image-001 through image-005.
- Preprocessing writes a mask and preprocess.json with experiment_id, image_id, mask_path, threshold, dimensions and foreground count.
- Inference consumes the image, mask metadata and a model path. It writes inference.json with experiment_id, image_id, foreground_fraction, mean_intensity and model_sha256.
- Aggregation reads one inference result per registered image. PostgreSQL table image_metrics has primary key (experiment_id, image_id).
- MongoDB database experiments, collection experiments, uses the experiment ID as _id. Completion sets status=COMPLETED and result_count=5.

Preserve these meanings when changing how services run. The generator stores model_path in data/manifest.json, and inference accepts --model-path. Dev owns these production steps. The team-support task asks you to publish a Data/ML artifact and expose its selection through configuration; no registry is required.

## Data/ML training example

The [supplied notebook and equivalent CLI](../examples/model_lifecycle/README.md) train a tiny regression model on synthetic data using NumPy. Run from the repository root:

~~~bash
python -m examples.model_lifecycle.train --output-dir data/model-lifecycle
~~~

This produces model.json and evaluation.json. The helpers supply training, benchmarking against a baseline, loading and prediction. Publication, release metadata, selection and rejection remain candidate work. Jupyter is optional; the CLI uses the same helpers as the notebook.

The image-inference mock can read this artifact and report its SHA-256, but its mask metrics do not evaluate the regression weights. Use the supplied model evaluation separately; do not claim production accuracy from the pipeline's completion status.

## Known limitations

The API and worker use fixed local storage paths. Local shared volumes are sufficient for the core assignment. The optional storage task replaces these paths with object access.

Preprocessing has a marked memory bottleneck. Optimizing it or measuring and sizing its container is optional. Model reads happen on every inference invocation; caching is optional.

Schema creation happens at runtime. PostgreSQL commits before MongoDB completion is updated, so an interruption can leave partial state. The optional recovery task explores this gap.

Generated metadata may contain absolute paths. When moving an existing host-generated data directory into containers, regenerate fixtures inside the container or map/update paths consistently.

The API has no authentication and Compose uses development credentials; keep the baseline local. Compose teardown removes its database containers; preserve anything needed before running:

~~~bash
docker compose down
~~~

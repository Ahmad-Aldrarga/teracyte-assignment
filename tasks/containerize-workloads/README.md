# Containerize the workloads

**Required task** · [Assignment](../../README.md) · [Starter guide](../../docs/local-development.md)

## Goal

Give Dev a repeatable runtime for its application and production analysis. Data/ML's training-to-model handoff is covered by the linked team-support task.

## Requirements

- Add Dockerfile(s) and extend Compose to run FastAPI, the Celery worker and the existing analysis runner with the supplied databases and Redis.
- One shared image with different commands is acceptable. A one-shot analysis container and sequential step execution are sufficient.
- Configure database/broker addresses through environment variables. Keep generated data and model weights in mounted storage, outside image layers; exclude them and secrets from the build context.
- Document startup, analysis and shutdown commands. Ensure dependencies are ready before analysis starts and analysis failures produce a nonzero exit code.

## Suggested starting point

Use requirements-local.txt and the commands in the starter guide. Inside containers, localhost refers to that container; use service names for dependencies. Share the required data paths between the runner, API and worker and ensure they are writable.

Keep model selection compatible with the [team-delivery task](../support-teams/README.md).

## How to demonstrate it

From a clean checkout, show the commands to build and start services, generate fixtures and complete one analysis run. Show the API returning its results and a queued Celery export producing a report. Record these in EVIDENCE.md.

## Optional improvements

Run as a non-root user, reduce image size, pin dependencies, add health checks, or measure resource use and set limits. Separate optimized step images are welcome but not required.

# DevOps & MLOps Engineer — Take-Home Assignment

You have **48 hours to submit**.

Start with a clean, working baseline. If a requirement is beyond your experience, implement a simplified version and explain the missing production work.

## The system

Camera images pass through preprocessing, mock model inference and database aggregation. MongoDB tracks experiments; PostgreSQL stores results. Dev owns the API, Celery and production analysis steps. Data/ML develops models through notebooks, training and benchmarking. DevOps/MLOps provides the infrastructure and model handoff between them. We run on Azure today and need cost-conscious, portable infrastructure.

## Start here

Follow the [local-development guide](docs/local-development.md) for the supplied services and [CPU training example](examples/model_lifecycle/README.md). Containerization, verification, CI, Terraform storage configuration and a small model handoff are your implementation tasks. The sequential analysis runner and local artifact publication are acceptable.

## Required tasks

### [Containerize the workloads](tasks/containerize-workloads/README.md)
- Run the API, worker and analysis pipeline with Compose.
- Configure connections externally; keep data and models outside images.

### [Verify an experiment](tasks/verify-experiment/README.md)
- Check five results, experiment status, model digest and execution time.
- Demonstrate one failing check.

### [Support notebook-to-model delivery and Dev](tasks/support-teams/README.md)
- Design portable cloud training and demonstrate a small local model handoff.
- Separate Dev's application/analysis delivery from Data/ML's model lifecycle.

### [Plan a cost-conscious cloud deployment](tasks/cloud-deployment/README.md)
- Map serving, analysis, notebook users and training to cloud infrastructure.
- Compare costs using the supplied worksheet and explain portability.

### [Implement storage with Terraform](tasks/cloud-infrastructure/README.md)
- Define private object storage and retention policies for your chosen cloud.
- Validate the configuration locally and in CI; cloud deployment is optional.

## Optional extensions

Choose only what interests you after the required work. Completing every extension is not expected.

- [Add Argo orchestration](tasks/argo-orchestration/README.md)
- [Implement a portable training and promotion platform](tasks/training-platform/README.md)
- [Add portable object storage and model caching](tasks/portable-storage-models/README.md)
- [Isolate shared development environments](tasks/dev-isolation/README.md)
- [Demonstrate failure recovery](tasks/failure-recovery/README.md)

## AI use and submission

**You are encouraged to use AI assistants. However, unverified, generic AI output will fail the review.**

Submit your repository with:
- **EVIDENCE.md:** exact run commands, relevant outputs, one failed verification and any setup limits.
- **ARCHITECTURE_AND_DECISIONS.md:** a short paragraph per major choice explaining why, one alternative and the trade-off. Include the cloud task's diagram/table and calculations here; no separate architecture essay is needed.

Explain one issue you encountered and how you verified the fix. Label estimates and incomplete work honestly. Keep generated data, model weights and credentials out of Git. We will discuss your working system, how it supports both teams, and the reasoning behind your cloud choices.

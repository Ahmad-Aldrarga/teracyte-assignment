# Support notebook-to-model delivery and the Dev team

**Required task — design plus a small local demonstration** · [Assignment](../../README.md)

## Goal

Dev owns the API, Celery and production analysis steps. Data/ML owns notebooks, datasets, training, evaluation, benchmarking and model candidates. DevOps/MLOps supplies reproducible environments and a clear handoff so Dev can integrate published models easily.

## Requirements

- Draw one workflow from notebook experimentation to reproducible training, experiment comparison, model publication and consumption by a Dev-owned analysis step. Include the cloud-training environment, CPU/GPU allocation, dataset access, credentials, artifact persistence and job cleanup.
- Define a model handoff with artifact location, release version, expected digest, input/output expectations and evaluation results. Explain promotion, rollback and the changes needed to move training/storage to another provider.
- Train/evaluate the supplied toy example locally, publish a selected artifact with your handoff metadata, and make that version available to the existing analysis pipeline through configuration. Demonstrate loading the toy artifact with its supplied helper and record the selected digest in the pipeline results.
- Reject one handoff, such as a digest mismatch or a failed evaluation threshold, before accepting that candidate for use. This can also be the required E2E failure demonstration only if the failing check prevents accepting or selecting that candidate. A digest assertion after the candidate has already been accepted is not a handoff gate.
- Add ci-core-dev.yml and ci-data-ml.yml under .github/workflows with the ownership and behavior below. Reuse local commands, propagate failures and retain useful logs.

| Change | Required delivery path |
|---|---|
| API, Celery or production analysis step | Dev workflow: relevant builds/tests, model-consumer compatibility and pipeline E2E checks when analysis/shared behavior changes |
| Terraform storage configuration | Dev workflow: formatting, initialization without a backend and validation; no cloud credentials or apply |
| Notebook, training or evaluation assets | Data/ML workflow: run training/evaluation, validate model candidates and demonstrate publication |
| Model-only candidate | Validate/publish the candidate and check its consumer contract without rebuilding the API; publication must not silently select it for production |
| Shared code, runtime or handoff contract | Both teams' relevant checks |

Local directory publication and metadata files are sufficient. A model-only workflow may reuse an existing consumer image or run lightweight supplied checks. A registry, paid cloud training, Kubernetes and a model-serving API are not required. Deployment here means making an approved version available to production analysis steps.

## Suggested starting point

Use the [supplied notebook and CLI example](../../examples/model_lifecycle/README.md); do not invent an ML algorithm. The same CPU helpers generate synthetic data, train, evaluate against a baseline and load an open JSON artifact. The CLI is sufficient if you do not have Jupyter installed.

Dev owns services/api and pipelines/steps. Data/ML's supplied starting assets are under examples/model_lifecycle. Classify shared scripts, dependencies and configuration explicitly. One shared Dockerfile remains acceptable.

The image-inference starter is a mock: it records the chosen artifact digest but does not evaluate the regression model. Prove selection/integration through the image pipeline and demonstrate toy-model evaluation separately using the supplied helpers. Production accuracy is outside this exercise.

Keep the design to a diagram and short notes. Use open artifact formats, configurable locations and portable training containers. Cloud provisioning may be provider-specific; training and consumption code must not depend on proprietary cloud ML APIs. Do not require Azure ML or another vendor-only registry to complete the workflow.

## How to demonstrate it

Include the training/evaluation command, benchmark result, published artifact/metadata, selected digest in pipeline results and one rejected handoff in EVIDENCE.md. Show which workflow owns application changes, analysis changes, training changes, model-only publication and shared changes.

Provide workflow run output. If repository permissions prevent Actions execution, include the workflow files, equivalent local output and the limitation. Reuse the cloud task's architecture diagram where useful rather than writing a second essay.

## Optional improvements

Implement the [training-platform bonus](../training-platform/README.md), publish immutable images, or add approval-based promotion. The required local demonstration does not need a full tracking/registry service.

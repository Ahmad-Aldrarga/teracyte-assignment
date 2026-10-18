# Add Argo as the analysis workflow orchestrator

**Optional task** · [Assignment](../../README.md)

## Goal

Run Dev's existing production analysis steps as a visible, repeatable Kubernetes workflow. Data/ML training infrastructure is a separate optional task.

## Requirements

If you choose this task:
- Add reproducible local Kubernetes and Argo setup. Kind/k3d is sufficient. Provisioning Kubernetes with Terraform or deploying it to the cloud is optional; the required Terraform task covers storage only. Compose may host supporting services, but Argo itself requires Kubernetes.
- Integrate the existing preprocess, inference and database-update commands with container inputs, outputs and database configuration.
- Add workflow-template.yaml accepting an experiment ID and image IDs. Preserve the image → mask → inference dependency and complete database aggregation only after the expected results exist.
- Add basic workflow monitoring: make terminal status, duration and failed-step logs accessible through a documented command or UI. Include resource requests/limits and bounded retries.

## Suggested starting point

First run a simple sequential workflow using the same fixtures and verifier as the required tasks. A shared local volume is acceptable for an initial implementation if its scheduling limitations are documented.

If you use Argo's S3 artifact repository, MinIO is suitable locally. Do not attempt to revive the removed MinIO Azure gateway. An in-cluster MinIO service is portable object storage in its own right.

## How to demonstrate it

Provide setup/submission commands, workflow YAML, one successful workflow's status/duration and access to its step logs. Run the database verifier against that experiment.

## Optional improvements

Fan out across images and fan in to a bounded aggregation step. Add artifact storage, dashboards, alerts or resource profiling. Explain how short-lived Pods can disappear between monitoring scrapes. A full monitoring stack is not necessary for the basic optional task.

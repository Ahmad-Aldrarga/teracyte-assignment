# Isolate shared development environments

**Optional task** · [Assignment](../../README.md)

## Goal

Let ten developers and data scientists test independently without paying for ten full clusters.

## Requirements

If you choose this task, provide either a detailed blueprint or working configuration covering:
- Unique service/workflow versions and a way to route requests or analysis to one developer's change.
- Isolation of database records, object keys and secrets where infrastructure is shared.
- Resource quotas and expiry/cleanup so idle environments do not accumulate costs.
- A workflow for Dev to change an API service or analysis step, and Data/ML to test a training run or candidate model, without overwriting another person's work.

## Suggested starting point

Namespaces or release names can separate deployments, but also explain data isolation and routing. A table showing Developer A and Developer B using different versions is sufficient for a blueprint.

## How to demonstrate it

Describe or run simultaneous A/B changes and show how their requests, outputs and resources remain distinguishable. Identify shared costs and which components scale down when idle.

## Optional improvements

Provide routing/network-policy manifests, preview environments, automatic expiry or per-developer usage reporting.

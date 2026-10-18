# Plan a cost-conscious cloud deployment

**Required task — design and calculation only** · [Assignment](../../README.md)

## Goal

Show practical cloud judgment for Dev's serving/analysis workloads and Data/ML's notebooks, training and model development.

## Requirements

In ARCHITECTURE_AND_DECISIONS.md, provide:
- One diagram or table placing the API, worker/broker, production batch analysis, notebook users, training workers, PostgreSQL, MongoDB, datasets and model artifacts. Choose Azure, AWS, GCP or a provider-neutral design; reuse the team-support diagram.
- Short explanations of which workloads need reliable capacity and which could use Spot/interruptible capacity or scale to zero.
- Two small calculations: storage policy comparison and compute/model-delivery comparison, using the worksheet below.
- A short migration outline for analysis, training and storage: configuration and credentials, data transfer, verification and rollback. Explain provider dependencies and likely operational work.
- Briefly discuss GPU utilization, idle-notebook shutdown and interrupted-training/checkpoint costs. No additional training-cost calculation is required.

No cloud account, deployment, price research or complete cloud bill is required. Implement the storage portion in the separate required [Terraform task](../cloud-infrastructure/README.md). This task also supplies the cloud reasoning for the decision log; do not write a duplicate essay.

## Suggested starting point

Use these **hypothetical exercise rates, not provider quotes**. Use binary units: 1 GiB = 1,024 MiB. Treat a month as 30 days.

### Calculation 1: storage

| Input | Assumption |
|---|---|
| Volume | 500,000 raw images/day; one mask per image |
| Size | Raw image 10 MiB; mask 1 MiB |
| Baseline | Raw images and masks remain hot for 30 days, then are deleted |
| Alternative | Raw images hot for 7 days, cool for 23 days, then deleted; masks hot for 30 days, then deleted |
| Rates | Hot $0.02/GiB-month; cool $0.01/GiB-month |

Calculate steady-state stored GiB and monthly storage cost for each policy, after retention has filled. Daily GiB × days retained gives the capacity in each tier; multiply that capacity by the tier's monthly rate. Do not multiply the monthly rate by 30 again. Report the monthly difference and one retrieval/retention trade-off.

### Calculation 2: production analysis compute and model delivery

| Input | Assumption |
|---|---|
| Production analysis workload (not training) | 100 node-hours/day before retries |
| On-Demand rate | $0.20/node-hour |
| Spot rate | $0.06/node-hour |
| Spot overhead | 20% extra node-hours for retries |
| Production model | 1.5 GiB |
| No cache | 2,000 model downloads/day |
| Cache | 4 cache warmups/day, one full model download per warmup |

Calculate monthly On-Demand and Spot compute cost, plus daily model-transfer GiB with and without the cache. Explain the likely startup benefit and cache loss on interrupted nodes. No transfer dollar price is supplied: identify where network charges might apply instead of inventing a quote.

These compute and download assumptions concern production analysis, not notebook or training usage. The 1.5 GiB model and image sizes are production assumptions; use the smaller supplied fixtures for implementation.

## How to demonstrate it

Show formulas, units, results and your recommendation. Identify omitted costs/risks such as requests, retrieval, egress, cluster/control-plane charges, database availability, backups and Spot interruptions.

Explain what changes when moving analysis, training and storage to another provider. Training and consumption code should remain provider-neutral; acknowledge any remaining coupling. Do not depend on Azure ML, CosmosDB-specific APIs, hardcoded Event Grid or direct Azure storage SDK calls in business logic. Explain how you would preserve open interfaces without requiring implementation of the optional storage task.

## Optional improvements

Use real dated pricing, estimate archive/retrieval or GPU costs, evaluate reserved capacity. These are not required calculations.

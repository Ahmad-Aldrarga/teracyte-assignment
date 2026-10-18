# Demonstrate failure recovery

**Optional task** · [Assignment](../../README.md)

## Goal

Recover from interruptions without duplicate results or misleading completion state.

## Requirements

If you choose this task:
- Inject a controlled process/container interruption during analysis or database aggregation.
- Demonstrate safe retry without duplicate PostgreSQL rows or false MongoDB completion.
- Show how completed inference output can be reused safely, accounting for image and model identity.
- Explain Celery export retries and what prevents conflicting or incomplete reports.

## Suggested starting point

Use the local runner and a process kill; Kubernetes and real Spot eviction are unnecessary. Inspect the existing upsert key and the gap between PostgreSQL commit and MongoDB update.

Choose one failure boundary and make it reproducible. Existing upserts help with duplicate rows, but do not by themselves prove recovery across both databases.

## How to demonstrate it

Record the failure, intermediate state, retry and final verification. Explain when cached/completed output is valid and when it must be recomputed.

## Optional improvements

Test additional failure boundaries, real Spot eviction, automatic resume, concurrent runs or an explicit reconciliation mechanism.

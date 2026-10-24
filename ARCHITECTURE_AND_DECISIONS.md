# Architecture and Decisions

## 1. Design Goals

The primary goal is to minimize recurring cloud costs while
preserving production reliability, security, and portability.

Cost optimization principles:
- Pay for compute only when workloads need it.
- Use Spot capacity for retryable batch workloads.
- Scale idle development and training resources to zero.
- Apply storage retention and tiering policies.
- Cache model artifacts to avoid repeated large downloads.
- Keep a small reliable capacity pool for critical services.

## 2. Azure Workload Placement

| Workload | Infrastructure | Cost Strategy |
|---|---|---|
| API | AKS reliable node pool | Small baseline, autoscaling |
| Celery worker and Redis broker | AKS / managed Redis | Scale workers based on queue depth |
| Production batch analysis | AKS Jobs on Spot nodes | Retry interrupted jobs |
| Notebook users | On-demand development compute | Automatic idle shutdown |
| Training workers | Kubernetes Jobs, CPU/GPU as needed | Scale to zero after completion |
| PostgreSQL | Managed PostgreSQL | Right-size capacity and backups |
| MongoDB | Managed MongoDB-compatible service | Right-size capacity and retention |
| Raw images and masks | Azure Blob Storage | Hot/Cool lifecycle and deletion |
| Datasets and model artifacts | Azure Blob Storage | Versioning and local model cache |

## 3. Main Trade-offs

AKS provides Kubernetes portability and workload isolation,
but has operational and baseline infrastructure costs.
Azure Container Apps may be cheaper for smaller deployments.

Spot VMs reduce batch compute costs but can be interrupted.
Jobs must support retries, idempotency, and checkpoints.

Managed databases reduce operational risk but cost more
than self-hosting. Production data reliability takes priority
over minimizing database costs.

Model caching reduces repeated downloads and startup delays.
Spot node replacement can invalidate local caches.

The final design must compare cost and reliability rather
than selecting the lowest price at the expense of availability.

## 4. Storage Cost Calculation

Exercise assumptions:
- 500,000 raw images per day
- Raw image: 10 MiB
- Mask: 1 MiB
- Retention: 30 days
- Hot storage: $0.02/GiB-month
- Cool storage: $0.01/GiB-month

Daily capacity:
- Raw images = 500,000 * 10 / 1024 = 4,882.8125 GiB/day
- Masks = 500,000 * 1 / 1024 = 488.28125 GiB/day

### Baseline: All Hot Storage

Total stored:
(4,882.8125 + 488.28125) * 30
= 161,132.8125 GiB

Monthly cost:
161,132.8125 * $0.02 = $3,222.66

### Optimized: Hot + Cool

Raw images:
- Hot for 7 days = 4,882.8125 * 7 = 34,179.6875 GiB
- Cool for 23 days = 4,882.8125 * 23 = 112,304.6875 GiB

Masks:
- Hot for 30 days = 488.28125 * 30 = 14,648.4375 GiB

Total Hot = 48,828.125 GiB
Total Cool = 112,304.6875 GiB
Total stored = 161,132.8125 GiB

Monthly cost:
(48,828.125 * $0.02) + (112,304.6875 * $0.01)
= $2,099.61

Monthly savings:
$3,222.66 - $2,099.61 = $1,123.05
Approximately 34.8% storage savings.

Trade-off:
Cool storage may introduce additional retrieval charges
and minimum retention or early-deletion charges.
Keep frequently accessed data Hot and validate actual
access patterns before applying lifecycle transitions.

## 5. Compute and Model Delivery Cost Calculation

Exercise assumptions:
- Production analysis: 100 node-hours/day
- On-Demand: $0.20/node-hour
- Spot: $0.06/node-hour
- Spot retry overhead: 20%
- Month: 30 days

### On-Demand

100 * 30 * $0.20 = $600/month

### Spot

100 * 1.20 * 30 * $0.06 = $216/month

Monthly savings:
$600 - $216 = $384
64% reduction in production analysis compute cost.

Use Spot only for restartable, idempotent batch jobs.
Retries, checkpointing, and fallback to reliable capacity
are required when Spot nodes are interrupted.

### Model Cache

Production model size: 1.5 GiB

Without cache:
2,000 downloads/day * 1.5 GiB
= 3,000 GiB/day

With cache:
4 warmups/day * 1.5 GiB
= 6 GiB/day

Reduction:
3,000 - 6 = 2,994 GiB/day (99.8%)

A model cache reduces repeated network transfers and
model startup delays. An interrupted Spot node can lose
its local cache, requiring a new warmup.

No network transfer price is supplied. Possible charges
include cross-region transfers and Internet egress.

### Cost Limitations

These estimates exclude:
- Kubernetes cluster and control-plane costs
- Database instances, backups, and high availability
- Storage requests and retrieval charges
- Network egress and private networking charges
- Monitoring, logging, and security services
- GPU training and notebook compute
- Spot availability and interruption variability

The numbers are exercise estimates, not Azure quotes.

## 6. Cloud Portability and Migration

The application should remain portable across Azure, AWS and GCP.
Use container images, Kubernetes Jobs, environment-based
configuration, and standard PostgreSQL and MongoDB interfaces.

### Configuration and Credentials

- Keep cloud endpoints and storage locations in configuration.
- Use workload identity and short-lived credentials where possible.
- Store secrets in a managed secret store, never in Git or images.
- Use separate Terraform modules for provider-specific resources.
- Keep cloud storage SDK details behind a storage adapter.

### Migration Steps

1. Provision the destination infrastructure using Terraform.
2. Create destination storage, databases and Kubernetes resources.
3. Configure destination credentials, endpoints and networking.
4. Copy datasets, images, masks and versioned model artifacts.
5. Verify object counts, checksums and model SHA-256 values.
6. Migrate database data using a consistent snapshot and
   change replication where supported.
7. Deploy API, workers, analysis Jobs and training Jobs.
8. Run integration and E2E checks in the destination environment.
9. Pause or drain writes, complete final synchronization,
   and verify consistency.
10. Gradually shift production traffic to the destination.

### Verification

- API readiness and health checks pass.
- PostgreSQL and MongoDB records are consistent.
- Analysis successfully processes five images.
- Model SHA-256 matches published metadata.
- Training produces a valid model artifact.
- Logs, metrics and alerts work in the new environment.

### Rollback

Keep the original infrastructure available during migration.

If verification fails before cutover, continue using the source
environment.

After cutover, stop destination writes before switching back.
Reconcile any new data written to the destination to prevent
data loss, then restore traffic to the source environment.

### Provider Dependencies

Azure AKS can be replaced by EKS or GKE.
Azure Blob Storage can be replaced by S3 or GCS.

The Kubernetes workloads and ML code remain largely unchanged,
but infrastructure modules, IAM, storage adapters, networking,
observability and managed database configuration require work.

Avoid Azure ML-specific APIs and direct cloud SDK usage inside
the analysis and training business logic.

## 7. GPU, Notebooks and Training Cost Control

### GPU Utilization

- Use CPU nodes when GPU acceleration is unnecessary.
- Schedule GPU workloads only on dedicated GPU node pools.
- Monitor GPU utilization and memory usage.
- Right-size GPU types based on measured workload requirements.
- Scale GPU worker capacity to zero when there are no jobs.

Trade-off: cold starts and node provisioning increase job latency.

### Idle Notebooks

- Automatically stop idle notebook environments.
- Store user files and checkpoints outside notebook containers.
- Apply CPU, memory and GPU resource quotas.
- Shut down development environments outside working hours
  when appropriate.

### Interrupted Training

Spot instances can reduce training cost, but interruptions
may lose progress and require additional compute time.

- Save periodic checkpoints to durable object storage.
- Resume from the latest compatible checkpoint.
- Record model version, dataset version and training parameters.
- Use reliable capacity when interruptions are too expensive.

Checkpoint frequency balances storage/write overhead against
the amount of training work lost during an interruption.

## 8. Final Recommendation

Prefer a small, reliable serving baseline with autoscaling.

Use interruptible capacity for retryable analysis and training.
Scale notebook and GPU resources to zero when idle.

Use lifecycle policies for image storage and cache large model
artifacts close to compute nodes.

Measure real usage before adding more infrastructure.
The cheapest architecture is not necessarily the one with
the lowest VM price if failures, retries and operational
overhead increase total costs.

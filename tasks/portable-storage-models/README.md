# Add portable object storage and model caching

**Optional task** · [Assignment](../../README.md)

## Goal

Implement portable artifact access and reduce repeated model downloads.

## Requirements

If you choose this task:
- Replace fixed storage paths with a configured abstraction or standard S3 access against MinIO.
- Use it for raw images, masks and model artifacts; document any remaining local-only outputs such as reports.
- Select immutable model content by version/digest and verify the expected digest.
- Demonstrate a reusable model cache or prewarming mechanism and explain its lifetime and invalidation.

## Suggested starting point

Use an established storage library or a small S3 helper. Keep endpoints, credentials and artifact locations in configuration. Provider adapter packages may live behind the abstraction; avoid provider SDK calls in business logic.

MinIO can run as portable object storage on any provider. No Azure Blob S3 gateway is required. Use the 50 MiB fixture; a production-size download is unnecessary.

## How to demonstrate it

Show an upload/read/write round trip, a model selection and two runs demonstrating reuse of cached content. Explain what happens when the selected digest changes or a cache entry is incomplete.

## Optional improvements

Add a model registry, concurrent cache-fill protection, per-team artifact isolation or cache metrics. Cover API/Celery exports through the same abstraction.

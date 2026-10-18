# Verify an experiment

**Required task** · [Assignment](../../README.md)

## Goal

Prove that the complete analysis writes correct results and that incorrect results fail visibly.

## Requirements

- Add tests/e2e_verify.py and one documented command that runs the analysis and verification against real PostgreSQL and MongoDB.
- For the current experiment, assert exactly five PostgreSQL rows with image-001 through image-005, MongoDB status COMPLETED and result_count=5.
- Assert that every result's model_sha256 matches an independently supplied expected digest. Compute it from the chosen fixture before execution or use a checked configuration value; do not derive the expectation from output rows.
- Measure elapsed pipeline time using a monotonic clock. Default to a 180-second timeout, excluding builds, fixture generation and dependency startup. Enforce termination/failure on timeout; a measured, documented adjustment is acceptable.
- Return nonzero on analysis failure, wrong results or timeout. Demonstrate one deliberately failing check.

## Suggested starting point

Reuse scripts/run_local.py and the database connection variables. Generate fixtures before starting the timer. Use a distinct experiment ID per verification run or explicitly clean its test state so stale results cannot satisfy the checks.

An intentionally wrong expected digest is enough for the failing demonstration. No chaos framework or database corruption is needed.

## How to demonstrate it

Include a successful five-image run with duration and a failing verification with its nonzero exit status in EVIDENCE.md. The [CI workflows](../support-teams/README.md) must reuse these commands.

## Optional improvements

Check metric values, add more negative cases, or collect memory/CPU measurements. Kubernetes, Argo and continuous cgroup scraping are not required.

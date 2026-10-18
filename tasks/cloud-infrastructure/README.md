# Implement storage with Terraform

**Required task — configuration and validation only** · [Assignment](../../README.md)

## Goal

Turn the storage portion of your cloud design into reviewable infrastructure code. No paid cloud account or Kubernetes experience is needed.

## Requirements

- Add Terraform under `infra/` using your chosen cloud provider. Define private object storage for raw images, masks and model artifacts, separated by containers/buckets or prefixes. Disable public access.
- Implement the worksheet's alternative retention policy: raw images hot for 7 days, then cool through day 30 and deleted; masks hot for 30 days and deleted. Exclude model artifacts from image-expiration rules. Explain provider minimum retention charges or lifecycle timing differences; use the worksheet's hypothetical rates for the calculation.
- Configure names, region and retention settings. Include useful storage location outputs and example inputs without credentials. Identify external dependencies.
- Declare Terraform and provider version constraints and commit `.terraform.lock.hcl`. Keep state, downloaded providers, secrets and saved plans out of Git.
- Briefly explain credentials, secure shared state and locking in production, expected charges, and what lifecycle expiration or cleanup would delete. Explain how provider-specific resources preserve the portable interfaces in your design.
- Run formatting and validation locally and in the Dev CI workflow. Cloud credentials, `plan` and `apply` are not required.

## Suggested starting point

Use the provider you know and implement storage only. A full network, cluster, database estate or remote-state backend implementation is unnecessary. Keep model retention separate from short-lived image retention.

Provider/module downloads need internet access. Initialization without a backend avoids connecting to remote state; validation does not verify cloud permissions, quotas, actual pricing or successful deployment.

## How to demonstrate it

From `infra/`, record these commands and their output in `EVIDENCE.md`:

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
```

Include example inputs and a short table mapping storage resources and lifecycle rules to raw images, masks and models. Reuse the cloud task's diagram. Document deployment and cleanup commands. Applying is not required; any optional deployment must use an account you are authorized to manage, with charges and cleanup documented. Disclose any validation blocked by network access instead of claiming it passed.

## Optional improvements

Implement compute, managed databases, AKS or another Kubernetes service, stable and Spot pools, workload identity or private networking. A cloud plan/apply and a secure remote-state backend are optional; describe any real deployment charges before running them.

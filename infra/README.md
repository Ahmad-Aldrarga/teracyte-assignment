# Azure Storage Infrastructure

## Overview

This Terraform configuration defines cost-conscious Azure Blob
Storage infrastructure for the TeraCyte assignment.

Resources:
- Azure Resource Group
- Azure Storage Account (Standard LRS, StorageV2)
- Private raw-images container
- Private masks container
- Private models container
- Azure Storage lifecycle management policy

No actual Azure resources are deployed as part of this submission.

## Storage Lifecycle

| Container | Storage Policy |
|---|---|
| raw-images | Hot for 7 days, Cool afterward, delete after 30 days |
| masks | Hot storage, delete after 30 days |
| models | No automatic deletion policy |

The lifecycle periods are configurable through Terraform variables.

The models container is excluded from automatic deletion to preserve
model artifacts and support rollback to earlier versions.

### Cost Considerations

Standard LRS minimizes storage replication cost compared with
higher-redundancy options, but provides less resilience against
regional failures.

Cool storage has minimum retention and early deletion charges.
Moving data to Cool after 7 days and deleting after 30 days may
therefore introduce early deletion charges.

Actual savings must account for storage, transactions, retrieval,
replication and networking charges.

## Security

- Anonymous blob access is disabled.
- All containers use private access.
- HTTPS is required.
- Minimum TLS version is 1.2.
- Shared account key authentication is disabled.
- Terraform uses Microsoft Entra ID for blob operations.
- No credentials or access keys are committed to Git.

Private container access does not disable the public network
endpoint. Production deployments should additionally restrict
network access using firewall rules or Private Endpoints.

Production workloads and Terraform deployment identities require
appropriate Azure RBAC roles.

## Requirements

- Terraform >= 1.6
- AzureRM provider 4.x
- Azure subscription and appropriate permissions for deployment

An Azure subscription is not required for formatting and
configuration validation.

## Validate Locally

Run from the repository root:

    terraform fmt -check -recursive infra/
    terraform -chdir=infra init -backend=false
    terraform -chdir=infra validate

These commands do not create Azure resources.

## Deployment Inputs

Configuration variables include:
- location
- resource_group_name
- storage_account_name
- raw_cool_after_days
- raw_delete_after_days
- masks_delete_after_days

The Storage Account name must be globally unique.

A real deployment also requires Azure authentication and an
Azure subscription ID for the AzureRM provider.

This assignment intentionally does not run terraform apply.

## Terraform State

Local state files must never be committed.

For production, use a remote Azure Blob Storage backend with:
- Microsoft Entra ID authentication
- Restricted RBAC permissions
- Encryption at rest
- Blob versioning and recovery protection where appropriate
- State locking using Azure Blob leases

Backend infrastructure should be provisioned separately.

The provider lock file .terraform.lock.hcl is committed to Git
for reproducible provider dependency selection.

## Production Considerations

- Choose redundancy based on recovery requirements and cost.
- Add Private Endpoints where network isolation is required.
- Monitor capacity, retrieval and transaction costs.
- Review lifecycle policies before changing retention.
- Use separate environments and Terraform state files.
- Review terraform plan before any real deployment.
- Back up important data before destructive infrastructure changes.

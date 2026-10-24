output "resource_group_name" {
  description = "Azure resource group"
  value       = azurerm_resource_group.storage.name
}

output "storage_account_name" {
  description = "Azure Storage Account name"
  value       = azurerm_storage_account.storage.name
}

output "blob_endpoint" {
  description = "Blob Storage endpoint"
  value       = azurerm_storage_account.storage.primary_blob_endpoint
}

output "container_names" {
  description = "Storage containers used by the application"

  value = {
    raw_images = azurerm_storage_container.raw_images.name
    masks      = azurerm_storage_container.masks.name
    models     = azurerm_storage_container.models.name
  }
}

resource "azurerm_storage_management_policy" "lifecycle" {
  storage_account_id = azurerm_storage_account.storage.id

  rule {
    name    = "raw-images-retention"
    enabled = true

    filters {
      blob_types   = ["blockBlob"]
      prefix_match = ["${azurerm_storage_container.raw_images.name}/"]
    }

    actions {
      base_blob {
        tier_to_cool_after_days_since_creation_greater_than = var.raw_cool_after_days
        delete_after_days_since_creation_greater_than       = var.raw_delete_after_days
      }
    }
  }

  rule {
    name    = "masks-retention"
    enabled = true

    filters {
      blob_types   = ["blockBlob"]
      prefix_match = ["${azurerm_storage_container.masks.name}/"]
    }

    actions {
      base_blob {
        delete_after_days_since_creation_greater_than = var.masks_delete_after_days
      }
    }
  }
}

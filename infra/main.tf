resource "azurerm_resource_group" "storage" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "storage" {
  name                = var.storage_account_name
  resource_group_name = azurerm_resource_group.storage.name
  location            = azurerm_resource_group.storage.location

  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  access_tier              = "Hot"

  min_tls_version                 = "TLS1_2"
  https_traffic_only_enabled      = true
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = false
  default_to_oauth_authentication = true

  tags = {
    project     = "teracyte-assignment"
    environment = "demo"
  }
}

resource "azurerm_storage_container" "raw_images" {
  name                  = "raw-images"
  storage_account_id    = azurerm_storage_account.storage.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "masks" {
  name                  = "masks"
  storage_account_id    = azurerm_storage_account.storage.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "models" {
  name                  = "models"
  storage_account_id    = azurerm_storage_account.storage.id
  container_access_type = "private"
}

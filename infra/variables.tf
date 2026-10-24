variable "location" {
  description = "Azure region for storage resources"
  type        = string
  default     = "westeurope"
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
  default     = "rg-teracyte-storage"
}

variable "storage_account_name" {
  description = "Globally unique Azure Storage Account name"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "Use 3-24 lowercase letters and numbers."
  }
}

variable "raw_cool_after_days" {
  description = "Move raw images to Cool after this many days"
  type        = number
  default     = 7
}

variable "raw_delete_after_days" {
  description = "Delete raw images after this many days"
  type        = number
  default     = 30
}

variable "masks_delete_after_days" {
  description = "Delete masks after this many days"
  type        = number
  default     = 30
}

variable "aws_region" {
  type        = string
  default     = "ap-south-1"
  description = "Deployment region (Mumbai by default)."
}
variable "project_name" {
  type    = string
  default = "linkdrop"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,18}$", var.project_name))
    error_message = "Use 3-19 lowercase letters, digits, or hyphens; start with a letter."
  }
}
variable "vpc_cidr" {
  type    = string
  default = "10.42.0.0/16"
}
variable "instance_type" {
  type        = string
  default     = "t3.micro"
  description = "Small burstable EC2 instance for a learning deployment."
}
variable "root_volume_gb" {
  type    = number
  default = 16
}
variable "compose_version" {
  type        = string
  default     = "v5.6.0"
  description = "Pinned Docker Compose CLI plugin release."
}
variable "github_owner" {
  type    = string
  default = "vlk-2805"
}
variable "github_repository" {
  type    = string
  default = "linkdrop"
}
variable "github_branch" {
  type    = string
  default = "main"
}
variable "github_owner_id" {
  type        = string
  default     = ""
  description = "Set with github_repository_id when GitHub uses immutable OIDC subjects."
}
variable "github_repository_id" {
  type        = string
  default     = ""
  description = "Set with github_owner_id when GitHub uses immutable OIDC subjects."
}

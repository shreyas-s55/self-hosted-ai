variable "name_prefix" {
  description = "Prefix for IAM resources"
  type        = string
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
}

variable "permissions_boundary_arn" {
  description = "Optional IAM permissions boundary ARN to attach to the EC2 role."
  type        = string
  default     = null
}
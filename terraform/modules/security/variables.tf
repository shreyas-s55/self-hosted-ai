variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the Security Group will be created"
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "CIDR blocks allowed to SSH"
  type        = list(string)
}

variable "web_allowed_cidr" {
  description = "CIDR blocks allowed to access the Web UI/API"
  type        = list(string)
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
}
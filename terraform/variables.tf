variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}


variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
}

variable "availability_zone" {
  description = "Availability Zone"
  type        = string
}

variable "name_prefix" {
  description = "Prefix for AWS resource names"
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "Allowed CIDRs for SSH"
  type        = list(string)
}

variable "web_allowed_cidr" {
  description = "Allowed CIDRs for Web access"
  type        = list(string)
}

variable "permissions_boundary_arn" {
  description = "Optional IAM permissions boundary ARN."
  type        = string
  default     = null
}

variable "enable_gpu" {
  description = "Enable GPU bootstrap"
  type        = bool
  default     = false
}

variable "instance_type" {
  type    = string
  default = "t3.large"
}

variable "use_spot_instance" {
  type    = bool
  default = false
}
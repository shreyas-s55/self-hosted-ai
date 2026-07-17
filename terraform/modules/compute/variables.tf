variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "subnet_id" {
  description = "Subnet where the EC2 instance will be launched"
  type        = string
}

variable "security_group_id" {
  description = "Security group attached to the EC2 instance"
  type        = string
}

variable "instance_profile_name" {
  description = "IAM Instance Profile attached to the EC2 instance"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string

  default = "g4dn.xlarge"
}

variable "root_volume_size" {
  description = "Root EBS volume size in GB"
  type        = number

  default = 100
}

variable "use_spot_instance" {
  description = "Launch as Spot Instance"

  type = bool

  default = true
}

variable "tags" {
  description = "Common resource tags"

  type = map(string)
}

variable "allocate_elastic_ip" {
  description = "Allocate and associate an Elastic IP"

  type = bool

  default = false
}
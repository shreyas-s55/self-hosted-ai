aws_region = "us-east-1"

project_name = "self-hosted-ai"
name_prefix  = "self-hosted-ai"

environment = "dev"

vpc_cidr = "10.0.0.0/16"

public_subnet_cidr = "10.0.1.0/24"

availability_zone = "us-east-1b"

permissions_boundary_arn = null

ssh_allowed_cidr = [
  "0.0.0.0/0"
]

web_allowed_cidr = [
  "0.0.0.0/0"
]

use_spot = false
instance_type = "g5.2xlarge"

enable_gpu = true
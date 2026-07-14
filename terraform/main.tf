module "network" {

  source = "./modules/network"

  project_name = var.project_name

  vpc_cidr = var.vpc_cidr

  public_subnet_cidr = var.public_subnet_cidr

  availability_zone = var.availability_zone

  tags = local.common_tags
}

module "identity" {

  source = "./modules/identity"

  name_prefix = var.name_prefix

  tags = local.common_tags
}
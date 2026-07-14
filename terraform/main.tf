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



module "security" {

  source = "./modules/security"

  name_prefix = var.name_prefix

  vpc_id = module.network.vpc_id

  ssh_allowed_cidr = var.ssh_allowed_cidr

  web_allowed_cidr = var.web_allowed_cidr

  tags = local.common_tags
}
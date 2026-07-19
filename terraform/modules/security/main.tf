resource "aws_security_group" "this" {

  name        = "${var.name_prefix}-sg"
  description = "Security Group for Self Hosted AI"
  vpc_id      = var.vpc_id

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-sg"
    }
  )

  #
  # SSH
  #
  ingress {
    description = "SSH"

    from_port = 22
    to_port   = 22
    protocol  = "tcp"

    cidr_blocks = var.ssh_allowed_cidr
  }

  #
  # HTTP (Caddy)
  #
  ingress {
    description = "HTTP"

    from_port = 80
    to_port   = 80
    protocol  = "tcp"

    cidr_blocks = var.web_allowed_cidr
  }

  #
  # HTTPS (Caddy / Let's Encrypt)
  #
  ingress {
    description = "HTTPS"

    from_port = 443
    to_port   = 443
    protocol  = "tcp"

    cidr_blocks = var.web_allowed_cidr
  }

  #
  # Temporary: direct access to Open WebUI during Caddy migration.
  # Remove this once Caddy is verified and all traffic goes through port 80/443.
  #
  ingress {
    description = "Temporary direct access during Caddy migration"

    from_port = 3000
    to_port   = 3000
    protocol  = "tcp"

    cidr_blocks = var.web_allowed_cidr
  }

  #
  # Allow all outbound traffic
  #
  egress {
    description = "Allow all outbound traffic"

    from_port = 0
    to_port   = 0
    protocol  = "-1"

    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }
}
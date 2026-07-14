resource "aws_security_group" "this" {

  name = "${var.name_prefix}-sg"

  description = "Security Group for Self Hosted AI"

  vpc_id = var.vpc_id

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-sg"
    }
  )
  ingress {

    description = "SSH"

    from_port = 22

    to_port = 22

    protocol = "tcp"

    cidr_blocks = var.ssh_allowed_cidr
  }

  ingress {

    description = "Open WebUI"

    from_port = 3000

    to_port = 3000

    protocol = "tcp"

    cidr_blocks = var.web_allowed_cidr
  }

  ingress {

    description = "vLLM API"

    from_port = 8000

    to_port = 8000

    protocol = "tcp"

    cidr_blocks = var.web_allowed_cidr
  }

  ingress {

    description = "HTTPS"

    from_port = 443

    to_port = 443

    protocol = "tcp"

    cidr_blocks = var.web_allowed_cidr
  }

  egress {

    description = "Allow all outbound traffic"

    from_port = 0

    to_port = 0

    protocol = "-1"

    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }
}
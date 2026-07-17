resource "aws_instance" "this" {

  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.security_group_id]
  iam_instance_profile   = var.instance_profile_name
  key_name               = aws_key_pair.this.key_name

  user_data = file("${path.module}/../../scripts/bootstrap.sh")

  associate_public_ip_address = true

  user_data_replace_on_change = true

  dynamic "instance_market_options" {
    for_each = var.use_spot_instance ? [1] : []

    content {
      market_type = "spot"

      spot_options {
        spot_instance_type = "one-time"
      }
    }
  }

  root_block_device {

    volume_size = var.root_volume_size
    volume_type = "gp3"

    encrypted = true

    delete_on_termination = true

  }

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  tags = merge(
    var.tags,
    {
      Name = local.instance_name
    }
  )

}
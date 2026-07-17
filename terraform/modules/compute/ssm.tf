resource "aws_ssm_parameter" "private_key" {

  name  = "/${var.name_prefix}/ssh/private-key"
  type  = "SecureString"
  value = tls_private_key.this.private_key_pem

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-private-key"
    }
  )
}

resource "aws_ssm_parameter" "public_key" {

  name  = "/${var.name_prefix}/ssh/public-key"
  type  = "String"
  value = tls_private_key.this.public_key_openssh

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-public-key"
    }
  )
}
resource "aws_eip" "this" {

  count = var.allocate_elastic_ip ? 1 : 0

  domain = "vpc"

  instance = aws_instance.this.id

  tags = merge(
    var.tags,
    {
      Name = "${local.instance_name}-eip"
    }
  )
}
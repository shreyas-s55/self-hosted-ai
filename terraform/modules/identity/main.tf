data "aws_iam_policy_document" "assume_role" {

  statement {

    effect = "Allow"

    principals {

      type = "Service"

      identifiers = [
        "ec2.amazonaws.com"
      ]
    }

    actions = [
      "sts:AssumeRole"
    ]
  }
}

resource "aws_iam_role" "this" {

  name = "${var.name_prefix}-ec2-role"

  assume_role_policy = data.aws_iam_policy_document.assume_role.json

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-ec2-role"
    }
  )
}

resource "aws_iam_role_policy_attachment" "ssm" {

  role = aws_iam_role.this.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "this" {

  name = "${var.name_prefix}-instance-profile"

  role = aws_iam_role.this.name

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-instance-profile"
    }
  )
}
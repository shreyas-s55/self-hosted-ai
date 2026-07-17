output "key_name" {
  value = aws_key_pair.this.key_name
}

output "instance_id" {
  value = aws_instance.this.id
}

output "public_ip" {
  value = aws_instance.this.public_ip
}

output "private_ip" {
  value = aws_instance.this.private_ip
}

output "ami_id" {
  value = data.aws_ami.ubuntu.id
}

output "private_key_parameter_name" {
  value = aws_ssm_parameter.private_key.name
}

output "public_key_parameter_name" {
  value = aws_ssm_parameter.public_key.name
}

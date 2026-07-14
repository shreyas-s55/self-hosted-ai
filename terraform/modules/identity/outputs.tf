output "instance_profile_name" {
  value = aws_iam_instance_profile.this.name
}

output "role_name" {
  value = aws_iam_role.this.name
}
variable "name_prefix" {
  description = "Prefix for IAM resources"
  type        = string
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
}
output "application_url" {
  description = "Public HTTP URL for the Linkdrop EC2 instance."
  value       = "http://${aws_instance.app.public_dns}"
}
output "ec2_instance_id" {
  description = "EC2 target used by the GitHub Actions SSM deployment."
  value       = aws_instance.app.id
}
output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}
output "github_actions_role_arn" {
  description = "Set as GitHub Actions variable AWS_ROLE_ARN."
  value       = aws_iam_role.github_deploy.arn
}
output "aws_region" {
  value = var.aws_region
}

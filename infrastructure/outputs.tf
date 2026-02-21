# Terraform Outputs

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.main.id
}

output "ec2_public_ip" {
  description = "EC2 Elastic IP address"
  value       = aws_eip.ec2.public_ip
}

output "ec2_public_dns" {
  description = "EC2 public DNS name"
  value       = aws_eip.ec2.public_dns
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.main.address
}

output "rds_port" {
  description = "RDS port"
  value       = aws_db_instance.main.port
}

output "ecr_backend_url" {
  description = "ECR Backend repository URL"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_url" {
  description = "ECR Frontend repository URL"
  value       = aws_ecr_repository.frontend.repository_url
}

output "sqs_queue_url" {
  description = "SQS events queue URL"
  value       = aws_sqs_queue.events.url
}

output "sqs_queue_arn" {
  description = "SQS events queue ARN"
  value       = aws_sqs_queue.events.arn
}

output "secrets_manager_arn" {
  description = "Secrets Manager secret ARN"
  value       = aws_secretsmanager_secret.app_secrets.arn
}

output "cloudwatch_log_group" {
  description = "CloudWatch Log Group name"
  value       = aws_cloudwatch_log_group.app.name
}

output "admin_group_name" {
  description = "IAM Admin group name (add users to this group)"
  value       = aws_iam_group.admins.name
}

output "github_actions_role_arn" {
  description = "GitHub Actions OIDC Role ARN (set as AWS_ROLE_ARN secret)"
  value       = aws_iam_role.github_actions.arn
}

# DNS Configuration instructions
output "dns_configuration" {
  description = "DNS records to configure"
  value = {
    type  = "A"
    name  = var.domain_name
    value = aws_eip.ec2.public_ip
    ttl   = 300
  }
}

# Summary
output "deployment_summary" {
  description = "Deployment summary"
  value = <<-EOT
    ===== SGCC AWS Infrastructure =====

    EC2 Instance:
      - Public IP: ${aws_eip.ec2.public_ip}
      - SSH: ssh -i <key.pem> ec2-user@${aws_eip.ec2.public_ip}

    RDS PostgreSQL:
      - Endpoint: ${aws_db_instance.main.address}
      - Port: ${aws_db_instance.main.port}
      - Database: ${var.db_name}

    ECR Repositories:
      - Backend: ${aws_ecr_repository.backend.repository_url}
      - Frontend: ${aws_ecr_repository.frontend.repository_url}

    SQS Queue:
      - URL: ${aws_sqs_queue.events.url}

    DNS Configuration:
      Point ${var.domain_name} A record to ${aws_eip.ec2.public_ip}

    Admin Group:
      - Name: ${aws_iam_group.admins.name}
      - Add IAM users to this group for admin access

    Next Steps:
      1. Update DNS records
      2. SSH to EC2 and configure SSL (certbot)
      3. Update GitHub Secrets for CI/CD
      4. Push code to trigger deployment
      5. Create IAM users and add to admin group
    ====================================
  EOT
}

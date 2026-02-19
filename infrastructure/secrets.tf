# AWS Secrets Manager for Application Secrets

resource "aws_secretsmanager_secret" "app_secrets" {
  name        = "${var.project_name}/app-secrets"
  description = "Application secrets for ${var.project_name}"

  tags = {
    Name = "${var.project_name}-app-secrets"
  }
}

# Generate random secrets for security
resource "random_password" "secret_key" {
  length  = 64
  special = true
}

resource "random_password" "grafana_password" {
  length  = 24
  special = true
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    # Database credentials
    POSTGRES_USER     = var.db_username
    POSTGRES_PASSWORD = var.db_password
    POSTGRES_DB       = var.db_name
    POSTGRES_HOST     = aws_db_instance.main.address
    POSTGRES_PORT     = "5432"
    DATABASE_URL      = "postgresql+asyncpg://${var.db_username}:${var.db_password}@${aws_db_instance.main.address}:5432/${var.db_name}"

    # Application secrets (auto-generated)
    SECRET_KEY        = random_password.secret_key.result
    CORS_ORIGINS      = "https://${var.domain_name},https://www.${var.domain_name}"

    # AWS resources
    SQS_QUEUE_URL     = aws_sqs_queue.events.url
    AWS_REGION        = var.aws_region

    # Grafana (auto-generated password)
    GRAFANA_ADMIN_USER     = "admin"
    GRAFANA_ADMIN_PASSWORD = random_password.grafana_password.result
  })

  depends_on = [aws_db_instance.main]
}

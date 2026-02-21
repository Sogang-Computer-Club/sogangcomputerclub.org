# AWS Secrets Manager - 애플리케이션 비밀 중앙 관리
# .env 파일이나 환경 변수에 비밀을 하드코딩하지 않고 안전하게 저장

resource "aws_secretsmanager_secret" "app_secrets" {
  name        = "${var.project_name}/app-secrets"
  description = "Application secrets for ${var.project_name}"

  tags = {
    Name = "${var.project_name}-app-secrets"
  }
}

# 보안 비밀 자동 생성 - 수동 설정 대신 Terraform이 강력한 랜덤 값 생성
resource "random_password" "secret_key" {
  length  = 64
  special = true
}

resource "random_password" "grafana_password" {
  length  = 24
  special = true
}

# 비밀 값 저장 - EC2 배포 스크립트에서 이 값을 조회하여 .env 생성
resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    # 데이터베이스 접속 정보 (RDS 주소 동적 참조)
    POSTGRES_USER     = var.db_username
    POSTGRES_PASSWORD = var.db_password
    POSTGRES_DB       = var.db_name
    POSTGRES_HOST     = aws_db_instance.main.address
    POSTGRES_PORT     = "5432"
    DATABASE_URL      = "postgresql+asyncpg://${var.db_username}:${var.db_password}@${aws_db_instance.main.address}:5432/${var.db_name}"

    # 앱 보안 설정 (자동 생성된 강력한 키)
    SECRET_KEY        = random_password.secret_key.result
    CORS_ORIGINS      = "https://${var.domain_name},https://www.${var.domain_name}"

    # AWS 리소스 정보
    SQS_QUEUE_URL     = aws_sqs_queue.events.url
    AWS_REGION        = var.aws_region

    # Grafana 관리자 계정 (자동 생성 비밀번호)
    GRAFANA_ADMIN_USER     = "admin"
    GRAFANA_ADMIN_PASSWORD = random_password.grafana_password.result
  })

  # RDS 생성 완료 후 주소 참조 가능
  depends_on = [aws_db_instance.main]
}

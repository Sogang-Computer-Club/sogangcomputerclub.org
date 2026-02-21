# RDS PostgreSQL 설정

# DB 서브넷 그룹 - Private 서브넷에 배치하여 외부 접근 차단
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

# RDS 파라미터 그룹 - PostgreSQL 튜닝 설정
resource "aws_db_parameter_group" "main" {
  family = "postgres15"
  name   = "${var.project_name}-db-params"

  # 모든 SQL 문 로깅 (디버깅/감사용)
  parameter {
    name  = "log_statement"
    value = "all"
  }

  # 1초 이상 걸리는 쿼리 로깅 (슬로우 쿼리 분석용)
  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  tags = {
    Name = "${var.project_name}-db-params"
  }
}

# RDS 인스턴스 - PostgreSQL 데이터베이스
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-db"

  # 엔진 설정
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = var.db_instance_class
  parameter_group_name = aws_db_parameter_group.main.name

  # 스토리지 - 자동 확장 활성화 (20GB 시작, 최대 100GB)
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true  # 저장 데이터 암호화 (규정 준수)

  # 데이터베이스 접속 정보
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  # 네트워크 - Private 서브넷에 배치, EC2에서만 접근 가능
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  # 고가용성 - Multi-AZ로 자동 장애 조치 (프로덕션 권장)
  multi_az = var.db_multi_az

  # 백업 - 1일 보관 (Free Tier 제한), 새벽 시간대 실행
  backup_retention_period = 1
  backup_window           = "03:00-04:00"        # UTC 기준
  maintenance_window      = "Mon:04:00-Mon:05:00"

  # 모니터링 - Performance Insights로 쿼리 성능 분석
  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  monitoring_interval                   = 60  # Enhanced Monitoring 1분 간격
  monitoring_role_arn                   = aws_iam_role.rds_monitoring.arn

  # 보호 설정
  auto_minor_version_upgrade = true   # 보안 패치 자동 적용
  deletion_protection        = true   # 실수로 삭제 방지 (콘솔에서 해제 후 삭제 가능)
  skip_final_snapshot        = false  # 삭제 시 최종 스냅샷 생성
  final_snapshot_identifier  = "${var.project_name}-db-final-snapshot"
  copy_tags_to_snapshot      = true

  tags = {
    Name = "${var.project_name}-db"
  }
}

# IAM Role for RDS Enhanced Monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "${var.project_name}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

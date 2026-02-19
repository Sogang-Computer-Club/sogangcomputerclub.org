# 보안 그룹 - AWS 방화벽 규칙

# EC2 보안 그룹 - 웹 트래픽 허용, SSH는 제한적 허용
resource "aws_security_group" "ec2" {
  name        = "${var.project_name}-ec2-sg"
  description = "Security group for EC2 instance"
  vpc_id      = aws_vpc.main.id

  # HTTP - Let's Encrypt 인증서 발급 및 HTTPS 리다이렉트용
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  # HTTPS - 실제 서비스 트래픽
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  # SSH - allowed_ssh_cidrs 미설정 시 규칙 생성 안됨 (보안 강화)
  # 0.0.0.0/0 대신 관리자 IP만 허용하여 브루트포스 공격 방지
  dynamic "ingress" {
    for_each = length(var.allowed_ssh_cidrs) > 0 ? [1] : []
    content {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = var.allowed_ssh_cidrs
      description = "SSH access from allowed IPs"
    }
  }

  # 아웃바운드 - 모든 트래픽 허용 (패키지 다운로드, API 호출 등)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name = "${var.project_name}-ec2-sg"
  }
}

# RDS 보안 그룹 - EC2에서만 접근 허용 (외부 직접 접근 불가)
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Security group for RDS instance"
  vpc_id      = aws_vpc.main.id

  # EC2 보안 그룹을 소스로 지정하여 해당 그룹의 인스턴스만 접근 허용
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2.id]
    description     = "PostgreSQL from EC2"
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}

# VPC 엔드포인트 보안 그룹 - VPC 내부 트래픽만 허용
# AWS 서비스(ECR, Secrets Manager 등) 호출 시 인터넷 경유 없이 AWS 내부망 사용
resource "aws_security_group" "vpc_endpoints" {
  name        = "${var.project_name}-vpc-endpoints-sg"
  description = "Security group for VPC endpoints"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "HTTPS from VPC"
  }

  tags = {
    Name = "${var.project_name}-vpc-endpoints-sg"
  }
}

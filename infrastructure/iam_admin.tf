# 관리자 IAM 그룹 설정
# 동아리 관리자(인수인계 대상)에게 서비스별 FullAccess 부여
# 사용법: AWS Console에서 IAM 사용자 생성 후 이 그룹에 추가

# 관리자 그룹
resource "aws_iam_group" "admins" {
  name = "${var.project_name}-admins"
}

# EC2 관리 (인스턴스 시작/중지, AMI 관리 등)
resource "aws_iam_group_policy_attachment" "admin_ec2" {
  group      = aws_iam_group.admins.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
}

# RDS 관리 (스냅샷, 파라미터 그룹 등)
resource "aws_iam_group_policy_attachment" "admin_rds" {
  group      = aws_iam_group.admins.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
}

# ECR 관리 (이미지 푸시/삭제, 레포지토리 관리)
resource "aws_iam_group_policy_attachment" "admin_ecr" {
  group      = aws_iam_group.admins.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
}

# SQS 관리 (큐 생성/삭제, 메시지 관리)
resource "aws_iam_group_policy_attachment" "admin_sqs" {
  group      = aws_iam_group.admins.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSQSFullAccess"
}

# Secrets Manager 관리 (시크릿 생성/수정)
resource "aws_iam_group_policy_attachment" "admin_secrets" {
  group      = aws_iam_group.admins.name
  policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
}

# CloudWatch 관리 (로그 조회, 알람 설정)
resource "aws_iam_group_policy_attachment" "admin_cloudwatch" {
  group      = aws_iam_group.admins.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchFullAccess"
}

# VPC 관리 (네트워크 설정 변경)
resource "aws_iam_group_policy_attachment" "admin_vpc" {
  group      = aws_iam_group.admins.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonVPCFullAccess"
}

# IAM 읽기 전용 (권한 확인용, 수정은 루트 계정에서)
resource "aws_iam_group_policy_attachment" "admin_iam_readonly" {
  group      = aws_iam_group.admins.name
  policy_arn = "arn:aws:iam::aws:policy/IAMReadOnlyAccess"
}

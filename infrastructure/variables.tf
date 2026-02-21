# Terraform 변수 정의
# terraform.tfvars 또는 환경 변수로 값 설정

variable "aws_region" {
  description = "AWS 리전 (서울)"
  type        = string
  default     = "ap-northeast-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "sgcc"
}

# VPC 네트워크 설정
variable "vpc_cidr" {
  description = "VPC CIDR 블록 (/16 = 65,536 IP)"
  type        = string
  default     = "10.0.0.0/16"
}

# EC2 인스턴스 설정
variable "ec2_instance_type" {
  description = "EC2 인스턴스 타입 (t3.small: 2vCPU, 2GB RAM, ~$15/월)"
  type        = string
  default     = "t3.small"
}

variable "ec2_key_name" {
  description = "EC2 SSH key pair name"
  type        = string
}

variable "ec2_volume_size" {
  description = "EC2 root volume size in GB"
  type        = number
  default     = 30
}

# RDS 데이터베이스 설정
variable "db_instance_class" {
  description = "RDS 인스턴스 클래스 (db.t4g.micro: 2vCPU, 1GB RAM, ~$13/월)"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "sgcc_db"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "sgcc_admin"
  sensitive   = true
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "db_multi_az" {
  description = "Enable Multi-AZ for RDS (동아리 규모에서는 불필요, 비용 2배)"
  type        = bool
  default     = false
}

# Domain Configuration
variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "sogangcomputerclub.org"
}

# SSH 접근 허용 IP (보안)
# 비어있으면 SSH 규칙이 생성되지 않음 (SSH 접근 불가)
# 본인 IP 확인: curl ifconfig.me
variable "allowed_ssh_cidrs" {
  description = "SSH 접근 허용 CIDR 목록 (예: [\"1.2.3.4/32\"])"
  type        = list(string)
  default     = []
}

# VPC 엔드포인트 (비용 vs 보안 트레이드오프)
# true: AWS 내부망으로 서비스 호출 (~$36/월 추가, 보안 강화)
# false: 인터넷 경유 (기본값, 비용 절감)
variable "enable_vpc_endpoints" {
  description = "VPC 인터페이스 엔드포인트 활성화 여부"
  type        = bool
  default     = false
}

# GitHub Actions OIDC
variable "github_repository" {
  description = "GitHub 레포지토리 (owner/repo 형식)"
  type        = string
  default     = "Sogang-Computer-Club/sogangcomputerclub.org"
}

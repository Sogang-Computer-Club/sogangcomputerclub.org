# 서강대학교 중앙컴퓨터동아리 웹사이트 AWS 인프라
# 아키텍처: EC2 + RDS (중간 티어, ~$56/월)

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  # S3 백엔드 사용 시 주석 해제 (팀 협업 시 상태 파일 공유 필요)
  # DynamoDB 테이블은 동시 apply 방지를 위한 락 용도
  # backend "s3" {
  #   bucket         = "sgcc-terraform-state"
  #   key            = "production/terraform.tfstate"
  #   region         = "ap-northeast-2"
  #   encrypt        = true
  #   dynamodb_table = "sgcc-terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  # 모든 리소스에 자동으로 태그 추가 (비용 추적 및 리소스 관리용)
  default_tags {
    tags = {
      Project     = "sogangcomputerclub"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# 데이터 소스 - AWS 계정/리전 정보 조회
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

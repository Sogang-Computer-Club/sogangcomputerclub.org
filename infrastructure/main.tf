# AWS Infrastructure for Sogang Computer Club Website
# Architecture: EC2 + RDS (Middle tier)

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

  # Uncomment to use S3 backend for state management
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

  default_tags {
    tags = {
      Project     = "sogangcomputerclub"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

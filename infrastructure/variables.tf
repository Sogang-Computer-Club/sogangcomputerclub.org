# Variables for AWS Infrastructure

variable "aws_region" {
  description = "AWS region"
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

# VPC Configuration
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

# EC2 Configuration
variable "ec2_instance_type" {
  description = "EC2 instance type"
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

# RDS Configuration
variable "db_instance_class" {
  description = "RDS instance class"
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
  description = "Enable Multi-AZ for RDS"
  type        = bool
  default     = true
}

# Domain Configuration
variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "sogangcomputerclub.org"
}

# Allowed IPs for SSH access
variable "allowed_ssh_cidrs" {
  description = "CIDR blocks allowed for SSH access"
  type        = list(string)
  default     = []  # Add your IP addresses for SSH access
}

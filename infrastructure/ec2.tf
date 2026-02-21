# EC2 인스턴스 설정

# 최신 Amazon Linux 2023 AMI 자동 조회
# AMI ID 하드코딩 대신 동적 조회로 보안 패치된 최신 이미지 사용
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# IAM Role for EC2
resource "aws_iam_role" "ec2" {
  name = "${var.project_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# EC2 IAM 정책 - 최소 권한 원칙 적용
# 각 AWS 서비스별로 필요한 최소한의 권한만 부여
resource "aws_iam_role_policy" "ec2" {
  name = "${var.project_name}-ec2-policy"
  role = aws_iam_role.ec2.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # ECR 인증 토큰 획득 (모든 레지스트리에 대해 필요)
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      },
      # ECR 이미지 풀 - 읽기 전용 (푸시 권한 없음)
      {
        Effect = "Allow"
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:DescribeImages"
        ]
        Resource = [
          aws_ecr_repository.backend.arn,
          aws_ecr_repository.frontend.arn
        ]
      },
      # SQS 이벤트 큐 접근
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:GetQueueUrl"
        ]
        Resource = aws_sqs_queue.events.arn
      },
      # Secrets Manager - 앱 비밀 조회만 허용
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.app_secrets.arn
      },
      # CloudWatch Logs - 앱 로그 전송
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
      }
    ]
  })
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "ec2" {
  name = "${var.project_name}-ec2-profile"
  role = aws_iam_role.ec2.name
}

# Elastic IP for EC2
resource "aws_eip" "ec2" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-ec2-eip"
  }
}

# EC2 인스턴스 - 애플리케이션 서버
resource "aws_instance" "main" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = var.ec2_instance_type
  key_name               = var.ec2_key_name
  subnet_id              = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.ec2.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name

  root_block_device {
    volume_size           = var.ec2_volume_size
    volume_type           = "gp3"      # gp2 대비 20% 저렴, IOPS/처리량 별도 설정 가능
    encrypted             = true       # 저장 데이터 암호화
    delete_on_termination = true       # 인스턴스 삭제 시 볼륨도 함께 삭제
  }

  # 초기 설정 스크립트 - Docker, AWS CLI 설치 및 앱 배포 환경 구성
  user_data = base64encode(templatefile("${path.module}/templates/user_data.sh", {
    aws_region     = var.aws_region
    ecr_registry   = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com"
    project_name   = var.project_name
    db_host        = aws_db_instance.main.address
    db_name        = var.db_name
    sqs_queue_url  = aws_sqs_queue.events.url
    secret_arn     = aws_secretsmanager_secret.app_secrets.arn
  }))

  tags = {
    Name = "${var.project_name}-ec2"
  }

  # RDS가 먼저 생성되어야 user_data에서 DB 주소 참조 가능
  depends_on = [aws_db_instance.main]
}

# Associate Elastic IP with EC2
resource "aws_eip_association" "ec2" {
  instance_id   = aws_instance.main.id
  allocation_id = aws_eip.ec2.id
}

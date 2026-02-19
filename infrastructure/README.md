# AWS Infrastructure for Sogang Computer Club Website

이 디렉토리는 Terraform을 사용한 AWS 인프라 코드를 포함합니다.

## 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                      AWS Cloud (ap-northeast-2)                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                        VPC (10.0.0.0/16)                      │  │
│  │  ┌─────────────────────────────────────────────────────────┐  │  │
│  │  │              Public Subnet (EC2 + Nginx)                │  │  │
│  │  └─────────────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────────────┐  │  │
│  │  │              Private Subnet (RDS PostgreSQL)            │  │  │
│  │  └─────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│  ┌──────────┐  ┌─────────────┐  ┌────────┐  ┌──────────────────┐   │
│  │   ECR    │  │   Secrets   │  │  SQS   │  │   CloudWatch     │   │
│  │ (Images) │  │   Manager   │  │(Events)│  │   (Monitoring)   │   │
│  └──────────┘  └─────────────┘  └────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## 사전 요구사항

1. **Terraform 설치** (>= 1.0)
   ```bash
   brew install terraform  # macOS
   ```

2. **AWS CLI 설치 및 설정**
   ```bash
   brew install awscli
   aws configure
   ```

3. **SSH 키 페어 생성** (AWS Console 또는 CLI)
   ```bash
   aws ec2 create-key-pair --key-name sgcc-key --query 'KeyMaterial' --output text > sgcc-key.pem
   chmod 400 sgcc-key.pem
   ```

## 배포 단계

### 1. 변수 설정

```bash
cp terraform.tfvars.example terraform.tfvars
```

`terraform.tfvars` 파일을 편집하여 값을 설정합니다:
- `ec2_key_name`: SSH 키 이름 (위에서 생성한 키)
- `db_password`: RDS 데이터베이스 비밀번호 (강력한 비밀번호 사용)
- `allowed_ssh_cidrs`: SSH 접근을 허용할 IP 주소들

### 2. Terraform 초기화 및 적용

```bash
cd infrastructure

# 초기화
terraform init

# 계획 검토
terraform plan

# 인프라 생성 (약 15-20분 소요)
terraform apply
```

### 3. 출력 확인

```bash
terraform output
```

주요 출력:
- `ec2_public_ip`: EC2 인스턴스 IP 주소
- `rds_endpoint`: RDS 엔드포인트
- `ecr_backend_url`: ECR 백엔드 저장소 URL
- `ecr_frontend_url`: ECR 프론트엔드 저장소 URL

### 4. DNS 설정

도메인 DNS 관리자에서 A 레코드 추가:
```
sogangcomputerclub.org  →  <ec2_public_ip>
www.sogangcomputerclub.org  →  <ec2_public_ip>
```

### 5. EC2 접속 및 초기 설정

```bash
ssh -i sgcc-key.pem ec2-user@<ec2_public_ip>

# 앱 디렉토리로 이동
cd /opt/sgcc

# 환경변수 로드
source .deploy-env

# docker-compose.aws.yml 복사 (GitHub에서)
# 수동으로 복사하거나 git clone 사용

# SSL 인증서 설정 (certbot)
sudo certbot certonly --webroot -w /var/www/html -d sogangcomputerclub.org -d www.sogangcomputerclub.org
```

### 6. GitHub Secrets 설정

GitHub 저장소 Settings → Secrets and variables → Actions에서 추가:

| Secret | 설명 |
|--------|------|
| `AWS_ROLE_ARN` | AWS IAM Role ARN (OIDC용) 또는 Access Keys 사용 |
| `ECR_BACKEND_REPO` | ECR 백엔드 저장소 이름 (예: `sgcc/backend`) |
| `ECR_FRONTEND_REPO` | ECR 프론트엔드 저장소 이름 (예: `sgcc/frontend`) |
| `EC2_HOST` | EC2 퍼블릭 IP 주소 |
| `EC2_USERNAME` | `ec2-user` |
| `EC2_SSH_KEY` | EC2 SSH 프라이빗 키 (PEM 형식) |

### 7. 배포 테스트

```bash
# GitHub에서 master 브랜치에 push하면 자동 배포
git push origin master
```

## 비용 예측

| 서비스 | 구성 | 월비용 (USD) |
|--------|------|--------------|
| EC2 | t3.small | ~$15 |
| EBS | 30GB gp3 | ~$3 |
| RDS PostgreSQL | db.t4g.micro, Multi-AZ | ~$30 |
| Elastic IP | 1개 | ~$4 |
| SQS | 저용량 | ~$1 |
| ECR | 이미지 저장 | ~$1 |
| Secrets Manager | 1개 비밀 | ~$2 |
| **총계** | | **~$56** |

## 관리 명령어

### 인프라 상태 확인
```bash
terraform show
```

### 인프라 변경 적용
```bash
terraform plan
terraform apply
```

### 인프라 삭제 (주의!)
```bash
# RDS의 deletion_protection을 먼저 비활성화해야 함
terraform destroy
```

### AWS Secrets Manager 비밀 업데이트
```bash
aws secretsmanager update-secret \
  --secret-id sgcc/app-secrets \
  --secret-string '{"SECRET_KEY":"your_new_secret",...}'
```

## 문제 해결

### EC2 접속 불가
1. Security Group에서 SSH (22번 포트) 허용 확인
2. `allowed_ssh_cidrs`에 본인 IP 추가

### RDS 연결 불가
1. Security Group에서 5432 포트가 EC2 Security Group에서만 허용되는지 확인
2. RDS가 private subnet에 있으므로 EC2를 통해서만 접근 가능

### 배포 실패
1. CloudWatch Logs 확인: `/aws/ec2/sgcc`
2. EC2에서 docker logs 확인:
   ```bash
   docker compose -f docker-compose.aws.yml logs backend
   ```

## 백업 및 복구

### RDS 자동 백업
- 7일간 자동 백업 활성화됨
- AWS Console에서 스냅샷 복원 가능

### 수동 스냅샷
```bash
aws rds create-db-snapshot \
  --db-instance-identifier sgcc-db \
  --db-snapshot-identifier sgcc-db-manual-backup
```

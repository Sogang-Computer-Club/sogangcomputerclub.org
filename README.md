# sogangcomputerclub.org

서강대학교 중앙컴퓨터동아리 SGCC의 공식 웹사이트입니다.

FastAPI + SvelteKit 기반으로 설계되었으며, AWS 클라우드 네이티브 아키텍처를 채택하고 있습니다.

## 목차

1. [아키텍처](#아키텍처)
2. [기술 스택](#기술-스택)
3. [개발 환경 설정](#개발-환경-설정)
4. [로컬 개발 가이드](#로컬-개발-가이드)
5. [테스트](#테스트)
6. [AWS 인프라 배포](#aws-인프라-배포)
7. [CI/CD 파이프라인](#cicd-파이프라인)
8. [운영 및 관리](#운영-및-관리)
9. [문제 해결](#문제-해결)
10. [기여하기](#기여하기)

---

## 아키텍처

### AWS 프로덕션 환경

```mermaid
flowchart TB
    subgraph Internet
        Users[Users]
    end

    subgraph AWS["AWS Cloud (ap-northeast-2)"]
        subgraph VPC["VPC (10.0.0.0/16)"]
            subgraph PublicSubnet["Public Subnet"]
                subgraph EC2["EC2 (t3.small)"]
                    subgraph Docker["docker-compose"]
                        Nginx["Nginx\n:80/443"]
                        Backend["Backend\nFastAPI :8000"]
                        Frontend["Frontend\nSvelteKit :3000"]
                        Redis["Redis\n:6379"]
                    end
                end
            end

            subgraph PrivateSubnet["Private Subnet"]
                RDS[("RDS PostgreSQL\nMulti-AZ")]
            end
        end

        ECR["ECR\n(Container Images)"]
        SQS["SQS\n(Event Queue)"]
        Secrets["Secrets Manager"]
        CloudWatch["CloudWatch\n(Monitoring)"]
    end

    Users -->|HTTPS| Nginx
    Nginx --> Backend
    Nginx --> Frontend
    Backend --> Redis
    Backend --> RDS
    Backend --> SQS
    Backend -.-> Secrets
    EC2 -.-> ECR
```

### 로컬 개발 환경

```mermaid
flowchart TB
    subgraph DockerCompose["docker-compose"]
        subgraph Services["Application Services"]
            Nginx["Nginx\n:80"]
            Backend["Backend\n:8000"]
            Frontend["Frontend\n:3000"]
        end

        subgraph DataStores["Data Stores"]
            Postgres[("PostgreSQL\n:5433")]
            Redis["Redis\n:6381"]
        end

        subgraph Messaging["Messaging"]
            Kafka["Kafka\n:9092"]
            Zookeeper["Zookeeper\n:2181"]
        end

        subgraph Monitoring["Monitoring"]
            Prometheus["Prometheus\n:9090"]
            Grafana["Grafana\n:3001"]
        end
    end

    Nginx --> Backend
    Nginx --> Frontend
    Backend --> Postgres
    Backend --> Redis
    Backend --> Kafka
    Kafka --> Zookeeper
    Prometheus --> Backend
    Grafana --> Prometheus
```

---

## 기술 스택

| 카테고리 | 기술 |
|----------|------|
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic, Uvicorn |
| Frontend | SvelteKit 2.0, Svelte 5, TypeScript, Tailwind CSS |
| Database | PostgreSQL 15 (AWS RDS Multi-AZ) |
| Cache | Redis 7 |
| Messaging | AWS SQS (프로덕션) / Apache Kafka (로컬) |
| Infrastructure | Terraform, Docker, Nginx |
| CI/CD | GitHub Actions, Amazon ECR |
| Monitoring | Prometheus, Grafana, AWS CloudWatch |

---

## 개발 환경 설정

### 필수 요구사항

- Python 3.13 이상
- Node.js 20 이상
- Docker 및 Docker Compose
- Git

### 1. 프로젝트 클론

```bash
git clone https://github.com/Sogang-Computer-Club/sogangcomputerclub.org.git
cd sogangcomputerclub.org
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 다음 값들을 설정합니다:

```bash
# Database Configuration
POSTGRES_USER=memo_user
POSTGRES_PASSWORD=your_secure_password    # 반드시 변경
POSTGRES_DB=memo_app
DATABASE_URL=postgresql+asyncpg://memo_user:your_secure_password@postgres:5432/memo_app

# Redis Configuration
REDIS_URL=redis://redis:6379

# Event Backend (kafka, sqs, null 중 선택)
EVENT_BACKEND=kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9093

# Security
SECRET_KEY=your_secret_key_here           # 반드시 변경
```

### 3. uv 패키지 매니저 설치 (Backend)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 4. 의존성 설치

```bash
# Backend 의존성
uv sync

# Frontend 의존성
cd frontend
npm install
cd ..
```

---

## 로컬 개발 가이드

### 방법 1: Docker Compose (권장)

모든 서비스를 한 번에 실행합니다.

```bash
# 전체 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend

# 서비스 중지
docker-compose down

# 볼륨까지 삭제 (DB 초기화)
docker-compose down -v
```

접속 주소:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서 (Swagger): http://localhost:8000/docs
- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090

### 방법 2: Backend 단독 실행

```bash
# 개발 서버 실행 (핫 리로드 활성화)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 특정 환경 변수와 함께
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5433/memo_app \
REDIS_URL=redis://localhost:6381 \
EVENT_BACKEND=null \
uv run uvicorn app.main:app --reload --port 8000
```

### 방법 3: Frontend 단독 실행

```bash
cd frontend

# 개발 서버 실행 (핫 리로드 활성화)
npm run dev

# 프로덕션 빌드
npm run build

# 빌드된 결과 실행
npm run preview
```

Frontend 개발 서버는 `/api/*` 요청을 자동으로 `http://localhost:8000`으로 프록시합니다.

### 데이터베이스 마이그레이션

Alembic을 사용하여 데이터베이스 스키마를 관리합니다.

```bash
# 마이그레이션 적용
uv run alembic upgrade head

# 새 마이그레이션 생성 (모델 변경 후)
uv run alembic revision --autogenerate -m "설명"

# 마이그레이션 롤백 (직전 버전)
uv run alembic downgrade -1

# 마이그레이션 히스토리 확인
uv run alembic history

# 현재 버전 확인
uv run alembic current
```

### 코드 스타일 및 린팅

```bash
# Backend 린팅 (Ruff)
uv run ruff check app/
uv run ruff format app/

# Frontend 타입 체크
cd frontend
npm run check
```

---

## 테스트

### Backend 단위 테스트

```bash
# 전체 테스트 실행
uv run pytest tests/ -v

# 특정 테스트 파일
uv run pytest tests/test_memos.py -v

# 특정 테스트 함수
uv run pytest tests/test_memos.py::test_create_memo -v

# 커버리지 리포트
uv run pytest tests/ --cov=app --cov-report=html
# htmlcov/index.html 에서 확인

# 통합 테스트 제외
uv run pytest tests/ --ignore=tests/integration -v
```

### Backend 통합 테스트

Docker 서비스가 실행 중이어야 합니다.

```bash
# Docker 서비스 시작
docker-compose up -d

# 서비스 준비 대기 (약 30초)
sleep 30

# 통합 테스트 실행
uv run pytest tests/integration/ -v

# 개별 통합 테스트
uv run pytest tests/integration/test_database.py -v
uv run pytest tests/integration/test_redis.py -v
uv run pytest tests/integration/test_kafka.py -v
uv run pytest tests/integration/test_api_e2e.py -v
```

### Frontend 테스트

```bash
cd frontend

# 전체 테스트 실행
npm run test

# 감시 모드 (파일 변경 시 자동 실행)
npm run test:watch

# 커버리지 리포트
npm run test:coverage
```

### 부하 테스트

```bash
# Locust Web UI 모드
uv run locust -f tests/load/locustfile.py --host=http://localhost:8000

# Headless 모드 (자동 실행)
uv run locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 1m \
  --headless
```

---

## AWS 인프라 배포

### 사전 요구사항

1. AWS 계정
2. AWS CLI 설정 완료 (`aws configure`)
3. Terraform 1.0 이상 설치
4. EC2 SSH 키 페어 생성

### 1. SSH 키 페어 생성

AWS Console에서 생성하거나 CLI 사용:

```bash
aws ec2 create-key-pair \
  --key-name sgcc-key \
  --query 'KeyMaterial' \
  --output text > sgcc-key.pem
chmod 400 sgcc-key.pem
```

### 2. Terraform 변수 설정

```bash
cd infrastructure
cp terraform.tfvars.example terraform.tfvars
```

`terraform.tfvars` 파일 편집:

```hcl
# AWS 설정
aws_region  = "ap-northeast-2"
environment = "production"

# EC2 설정
ec2_instance_type = "t3.small"
ec2_key_name      = "sgcc-key"        # 위에서 생성한 키 이름
ec2_volume_size   = 30

# RDS 설정
db_instance_class = "db.t4g.micro"
db_name           = "sgcc_db"
db_username       = "sgcc_admin"
db_password       = "YourSecurePassword123!"  # 강력한 비밀번호 사용
db_multi_az       = true

# 도메인
domain_name = "sogangcomputerclub.org"

# SSH 접근 허용 IP (본인 IP 추가)
allowed_ssh_cidrs = ["123.456.789.0/32"]

# VPC 엔드포인트 (비용 절감을 위해 기본 비활성화)
enable_vpc_endpoints = false
```

### 3. 인프라 생성

```bash
cd infrastructure

# Terraform 초기화
terraform init

# 실행 계획 확인
terraform plan

# 인프라 생성 (약 15-20분 소요)
terraform apply

# 출력값 확인
terraform output
```

### 4. DNS 설정

도메인 DNS 관리자에서 A 레코드를 추가합니다:

```
sogangcomputerclub.org      A    <EC2_PUBLIC_IP>
www.sogangcomputerclub.org  A    <EC2_PUBLIC_IP>
```

EC2 Public IP는 `terraform output ec2_public_ip` 명령으로 확인할 수 있습니다.

### 5. EC2 초기 설정

```bash
# EC2 접속
ssh -i sgcc-key.pem ec2-user@<EC2_PUBLIC_IP>

# 앱 디렉토리 이동
cd /opt/sgcc

# 환경변수 로드
source .deploy-env

# docker-compose.aws.yml 복사 (GitHub에서)
# git clone 또는 수동 복사

# 배포 스크립트 실행
./deploy.sh
```

### 6. SSL 인증서 설정

```bash
# EC2에서 root 권한으로 실행
sudo /opt/sgcc/scripts/setup-ssl.sh sogangcomputerclub.org admin@sogangcomputerclub.org
```

### 7. GitHub Secrets 설정

GitHub Repository Settings > Secrets and variables > Actions에 추가:

| Secret | 설명 | 예시 |
|--------|------|------|
| `AWS_ROLE_ARN` | AWS IAM Role ARN (OIDC용) | `arn:aws:iam::123456789:role/github-actions` |
| `ECR_BACKEND_REPO` | ECR 백엔드 저장소 이름 | `sgcc/backend` |
| `ECR_FRONTEND_REPO` | ECR 프론트엔드 저장소 이름 | `sgcc/frontend` |
| `EC2_HOST` | EC2 퍼블릭 IP | `1.2.3.4` |
| `EC2_USERNAME` | EC2 사용자 | `ec2-user` |
| `EC2_SSH_KEY` | EC2 SSH 프라이빗 키 (PEM 내용 전체) | `-----BEGIN RSA...` |

### 예상 월 비용

| 서비스 | 구성 | 월 비용 (USD) |
|--------|------|---------------|
| EC2 | t3.small (2vCPU, 2GB) | ~15 |
| EBS | 30GB gp3 | ~3 |
| RDS PostgreSQL | db.t4g.micro, Multi-AZ | ~30 |
| Elastic IP | 1개 | ~4 |
| SQS | 저용량 | ~1 |
| ECR | 이미지 저장 | ~1 |
| Secrets Manager | 1개 비밀 | ~2 |
| 총계 | | ~56 |

VPC 엔드포인트 활성화 시 약 $36/월 추가됩니다.

---

## CI/CD 파이프라인

### 워크플로우 구성

| 워크플로우 | 파일 | 트리거 | 설명 |
|------------|------|--------|------|
| Backend CI | `backend-ci.yml` | Push, PR | Python 테스트, 린팅, 커버리지 |
| Frontend CI | `frontend-ci.yml` | Push, PR | TypeScript 체크, 테스트, 빌드 |
| AWS 배포 | `deploy-aws.yml` | master push | ECR 빌드, EC2 배포 |
| 보안 스캔 | `security-scan.yml` | Push, 매일 | Trivy, CodeQL, TruffleHog |
| 통합 테스트 | `integration-tests.yml` | Push, PR | Docker 서비스 연동 테스트 |

### AWS 배포 플로우

```mermaid
flowchart TD
    A[master 브랜치 Push] --> B{Security Scan}
    B -->|CRITICAL 취약점| X[배포 중단]
    B -->|통과| C[Build Docker Images]
    C --> D[Push to ECR]
    D --> E[Deploy to EC2]
    E --> F[docker-compose pull]
    F --> G[docker-compose up -d]
    G --> H{Smoke Tests}
    H -->|성공| I[배포 완료]
    H -->|실패| J[Auto Rollback]
    J --> K[latest 태그로 복원]
```

### 수동 배포

```bash
# GitHub Actions UI에서 workflow_dispatch 트리거
# 또는 EC2에서 직접 실행

ssh -i sgcc-key.pem ec2-user@<EC2_IP>
cd /opt/sgcc
source .deploy-env
./deploy.sh
```

---

## 운영 및 관리

### 서비스 상태 확인

```bash
# EC2 접속
ssh -i sgcc-key.pem ec2-user@<EC2_IP>

# 컨테이너 상태 확인
docker compose -f docker-compose.aws.yml ps

# 서비스 로그 확인
docker compose -f docker-compose.aws.yml logs -f backend
docker compose -f docker-compose.aws.yml logs -f frontend
docker compose -f docker-compose.aws.yml logs -f nginx

# 헬스 체크
curl http://localhost:8000/health
curl http://localhost:3000
```

### 서비스 재시작

```bash
# 전체 재시작
docker compose -f docker-compose.aws.yml restart

# 개별 서비스 재시작
docker compose -f docker-compose.aws.yml restart backend
docker compose -f docker-compose.aws.yml restart frontend

# 완전 재배포 (이미지 다시 pull)
docker compose -f docker-compose.aws.yml pull
docker compose -f docker-compose.aws.yml up -d
```

### 로그 관리

```bash
# 최근 100줄 로그
docker compose -f docker-compose.aws.yml logs --tail 100 backend

# 실시간 로그 (Ctrl+C로 종료)
docker compose -f docker-compose.aws.yml logs -f backend

# CloudWatch Logs (AWS Console에서 확인)
# 로그 그룹: /aws/ec2/sgcc
```

### 데이터베이스 관리

```bash
# RDS 접속 (EC2에서만 가능)
psql -h <RDS_ENDPOINT> -U sgcc_admin -d sgcc_db

# 백업 생성 (AWS Console 또는 CLI)
aws rds create-db-snapshot \
  --db-instance-identifier sgcc-db \
  --db-snapshot-identifier sgcc-db-backup-$(date +%Y%m%d)

# 스냅샷 목록 확인
aws rds describe-db-snapshots --db-instance-identifier sgcc-db
```

### Secrets Manager 업데이트

```bash
# 현재 비밀 확인
aws secretsmanager get-secret-value \
  --secret-id sgcc/app-secrets \
  --query 'SecretString' \
  --output text | jq

# 비밀 업데이트
aws secretsmanager update-secret \
  --secret-id sgcc/app-secrets \
  --secret-string '{"SECRET_KEY":"new_value",...}'

# EC2에서 비밀 새로고침
ssh ec2-user@<EC2_IP>
cd /opt/sgcc
./fetch-secrets.sh "$SECRET_ARN" "$AWS_REGION" .env
docker compose -f docker-compose.aws.yml restart
```

### SSL 인증서 갱신

Certbot이 자동으로 갱신하지만, 수동으로 확인하려면:

```bash
# 인증서 상태 확인
sudo certbot certificates

# 수동 갱신 (테스트)
sudo certbot renew --dry-run

# 실제 갱신
sudo certbot renew
```

### 모니터링

- CloudWatch Alarms: AWS Console에서 확인
  - EC2 CPU 사용률 > 80%
  - RDS CPU 사용률 > 80%
  - RDS 스토리지 < 5GB
  - SQS DLQ 메시지 > 0

- Grafana (로컬 개발 환경): http://localhost:3001
- Prometheus (로컬 개발 환경): http://localhost:9090

### 인프라 변경

```bash
cd infrastructure

# 변경 사항 확인
terraform plan

# 변경 적용
terraform apply

# 특정 리소스만 재생성
terraform taint aws_instance.main
terraform apply
```

### 인프라 삭제 (주의)

```bash
# RDS deletion_protection 비활성화 필요
# AWS Console에서 RDS > Modify > Deletion protection 해제

cd infrastructure
terraform destroy
```

---

## 문제 해결

### 포트 충돌

```bash
# 기존 컨테이너 확인
docker ps -a

# SGCC 관련 컨테이너 정리
docker ps -aq --filter name=sgcc | xargs -r docker rm -f
docker ps -aq --filter name=sogangcomputercluborg | xargs -r docker rm -f
```

### SSH 접속 불가

1. Security Group 확인: `allowed_ssh_cidrs`에 본인 IP가 포함되어 있는지 확인
2. 미설정 시 SSH 규칙이 생성되지 않음 (보안 목적)
3. AWS Console > EC2 > Security Groups에서 인바운드 규칙 확인

### RDS 연결 불가

1. RDS는 Private Subnet에 있어 EC2를 통해서만 접근 가능
2. Security Group에서 5432 포트가 EC2 Security Group에서만 허용되는지 확인
3. RDS 엔드포인트 확인: `terraform output rds_endpoint`

### 배포 실패

```bash
# EC2에서 디버깅
ssh ec2-user@<EC2_IP>
cd /opt/sgcc

# 컨테이너 상태 확인
docker compose -f docker-compose.aws.yml ps

# 로그 확인
docker compose -f docker-compose.aws.yml logs --tail 100 backend

# 환경변수 확인
cat .env

# 수동 재배포
./deploy.sh
```

### SSL 인증서 발급 실패

1. DNS A 레코드가 EC2 IP를 가리키는지 확인
2. 80번 포트가 열려 있는지 확인
3. Nginx가 실행 중인지 확인

```bash
# Nginx 상태 확인
docker compose -f docker-compose.aws.yml ps nginx

# 임시로 Nginx 중지 후 인증서 발급
docker compose -f docker-compose.aws.yml stop nginx
sudo certbot certonly --standalone -d sogangcomputerclub.org
docker compose -f docker-compose.aws.yml start nginx
```

---

## 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

코드 스타일:
- Backend: Ruff 린터 사용 (`uv run ruff check app/`)
- Frontend: Prettier, ESLint 사용 (`npm run check`)
- 커밋 메시지: Conventional Commits 형식 권장

자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md) 및 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)를 참조하세요.

---

## 라이선스

MIT License - [LICENSE](LICENSE) 참조

---

## 개발팀

### Infra/Database
- 조준희 (19 중국문화학과)

### Backend
- 김대원 (23 경제학과)
- 조준희 (19 중국문화학과)

### Frontend
- 김대원 (23 경제학과)
- 김주희 (24 미디어 엔터테인먼트)
- 정주원 (24 물리학과)
- 조인영 (25 인문 기반 자율전공)
- 허완 (25 컴퓨터공학과)

---

Made by SGCC

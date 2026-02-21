# SGCC 개발 문서

서강대학교 중앙컴퓨터동아리 웹사이트 개발을 위한 기술 문서입니다.

## 문서 목록

### 시작하기

- [개발 환경 설정](./getting-started.md) - 로컬 개발 환경 구축

### 아키텍처

- [시스템 아키텍처](./architecture.md) - 전체 시스템 구조 및 설계 원칙

### 개발 가이드

- [백엔드 개발](./backend.md) - FastAPI, SQLAlchemy, 도메인 구조
- [프론트엔드 개발](./frontend.md) - SvelteKit, Svelte 5, 컴포넌트 패턴
- [API 레퍼런스](./api-reference.md) - REST API 엔드포인트 명세

### 인프라 및 배포

- [인프라 설정](./infrastructure.md) - Terraform, AWS 리소스
- [배포 가이드](./deployment.md) - CI/CD, 프로덕션 배포

### 품질 관리

- [테스트 가이드](./testing.md) - 단위 테스트, 통합 테스트, 부하 테스트
- [문제 해결](./troubleshooting.md) - 일반적인 오류와 해결 방법

## 기술 스택

| 영역           | 기술                                                |
| -------------- | --------------------------------------------------- |
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.0, Pydantic |
| Frontend | SvelteKit 2.0, Svelte 5, TypeScript, Tailwind CSS |
| Database | PostgreSQL 15 (AWS RDS) |
| Infrastructure | Terraform, Docker, Nginx |
| CI/CD | GitHub Actions, Amazon ECR |
| Monitoring | Prometheus, Grafana, AWS CloudWatch |

> **Note**: 동아리 규모에서 불필요한 기술은 제외됨:
>
> - Redis (캐싱) - Rate limiting은 in-memory 사용
> - Kafka/SQS (메시징) - 이벤트 시스템 기본 비활성화 (`EVENT_BACKEND=null`)
> - RDS Multi-AZ - 고가용성 불필요

## 빠른 시작

```bash
# 프로젝트 클론
git clone https://github.com/Sogang-Computer-Club/sogangcomputerclub.org.git
cd sogangcomputerclub.org

# 환경 변수 설정
cp .env.example .env

# Docker로 핵심 서비스 실행
docker-compose up -d

# 모니터링 포함 실행
docker-compose --profile monitoring up -d

# 접속
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API 문서: http://localhost:8000/docs
```

## 프로젝트 구조

```text
sogangcomputerclub.org/
├── app/                    # 백엔드 애플리케이션
│   ├── core/              # 공통 인프라 (config, database, security)
│   ├── memos/             # 메모 도메인
│   ├── users/             # 사용자 도메인
│   ├── health/            # 헬스체크
│   └── events/            # 이벤트 발행
├── frontend/              # 프론트엔드 애플리케이션
│   └── src/
│       ├── routes/        # 페이지 라우트
│       └── lib/           # 컴포넌트, 스토어, 유틸
├── infrastructure/        # Terraform 인프라 코드
├── tests/                 # 백엔드 테스트
├── docs/                  # 개발 문서 (현재 위치)
└── .github/workflows/     # CI/CD 파이프라인
```

## 기여하기

1. 이슈를 확인하거나 새로 생성합니다
2. 피처 브랜치를 생성합니다 (`git checkout -b feature/기능명`)
3. 변경사항을 커밋합니다 (`git commit -m '기능 설명'`)
4. 브랜치를 푸시합니다 (`git push origin feature/기능명`)
5. Pull Request를 생성합니다

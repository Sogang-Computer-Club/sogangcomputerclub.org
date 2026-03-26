# CLAUDE.md

## Project Overview
서강대학교 컴퓨터 동아리 웹사이트 (소규모 프로젝트)

## Tech Stack
- Backend: FastAPI + SQLAlchemy 2.0 + PostgreSQL
- Frontend: SvelteKit 5 + Tailwind CSS v4
- Infra: Docker Compose (로컬), AWS EC2+RDS (프로덕션)
- CI/CD: GitHub Actions

## Commands
- `docker-compose up` - 핵심 서비스만 (backend, postgres, frontend, nginx)
- `docker-compose --profile monitoring up` - Prometheus+Grafana 포함
- `uv sync` - Python 의존성 설치
- `cd frontend && npm install` - 프론트엔드 의존성 설치
- `uv run pytest tests/ -v` - 백엔드 테스트
- `uv run ruff check app/` - 백엔드 린트
- `cd frontend && npm run check` - 프론트엔드 타입 체크
- `pre-commit run --all-files` - 전체 pre-commit 훅 실행
- `./scripts/check.sh` - 로컬 CI 검증 (backend|frontend|all)
- `cd frontend && npm run cz` - 대화형 커밋 메시지 작성

## Documentation
- `README.md` - 프로젝트 소개용 (외부 공개)
- `/docs/` - 개발 문서, 인수인계용 (내부 개발자용)

## Open Source Files
- `LICENSE` - MIT License
- `CONTRIBUTING.md` - 기여 가이드 (GitHub Flow)
- `CODE_OF_CONDUCT.md` - 행동 강령
- `SECURITY.md` - 보안 취약점 신고
- `.github/ISSUE_TEMPLATE/` - 이슈 템플릿 (bug, feature)
- `.github/PULL_REQUEST_TEMPLATE.md` - PR 템플릿
- `.github/labeler.yml` - PR 자동 라벨링 규칙
- `docs/github-labels.md` - 라벨 목록 및 사용법

## Architecture Notes
- Rate Limiting: in-memory storage (Redis 불필요)
- Repository 패턴 사용 (app/core/repository.py)

## Maintenance Notes
- 의존성 제거 시 `.github/workflows/` 와 `tests/` 디렉토리도 함께 정리할 것
- GitHub Actions script 블록에서 JS 템플릿 리터럴 사용 시 문자열 연결 방식 사용 (YAML 파서 충돌 방지)
- Alpine Docker: `addgroup --gid 1000` 대신 `addgroup -S` 사용 (GID 충돌 방지)
- CI 테스트 시 `DEBUG=true` 환경변수 필요 (프로덕션 검증 우회)
- pre-commit ruff 버전과 pyproject.toml ruff 버전 동기화 필요 (포맷팅 루프 방지)
- SvelteKit: 빌드 시점 환경변수는 `$env/dynamic/private` 사용 (Docker 빌드 호환)
- Alembic은 dev 의존성 — 프로덕션 컨테이너에서 `alembic` 명령 사용 불가
- DB 테이블 생성 시 모델 import 필수: `from app.memos.models import memos` (metadata만 import하면 테이블 미등록)
- deploy-aws.yml은 Alembic 마이그레이션 미실행 — 새 테이블은 수동 생성 필요
- `infrastructure/terraform.tfvars`의 `github_repository`는 org repo 이름과 일치해야 함 (OIDC 인증)
- AWS 작업 전 `aws sts get-caller-identity`로 올바른 계정 확인 (인프라: 567886497655)

## Scale Guidelines

동아리 규모 (수십~수백 명)에서 불필요한 것들:

- Redis 캐싱
- RDS Multi-AZ
- 과도한 CI 워크플로우 (auto-merge, stale 등)

## AWS Free Tier
- EC2: t3.micro (1GB RAM)
- RDS: db.t3.micro (1GB RAM)
- 현재 인프라: `infrastructure/terraform.tfvars` 참조

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
- `docker-compose --profile kafka up` - Kafka 이벤트 포함
- `docker-compose --profile monitoring up` - Prometheus+Grafana 포함
- `uv sync` - Python 의존성 설치
- `cd frontend && pnpm install` - 프론트엔드 의존성 설치
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
- 이벤트 시스템: 기본 비활성화 (EVENT_BACKEND=null), 필요시 kafka/sqs 활성화
- Rate Limiting: in-memory storage (Redis 불필요)
- Repository 패턴 사용 (app/core/repository.py)

## Maintenance Notes
- 의존성 제거 시 `.github/workflows/` 와 `tests/` 디렉토리도 함께 정리할 것

## Scale Guidelines
동아리 규모 (수십~수백 명)에서 불필요한 것들:
- Kafka/SQS 이벤트 시스템
- Redis 캐싱
- RDS Multi-AZ
- 과도한 CI 워크플로우 (auto-merge, stale 등)

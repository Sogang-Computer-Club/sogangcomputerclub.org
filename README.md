# sogangcomputerclub.org

서강대학교 중앙컴퓨터동아리 SGCC의 공식 웹사이트입니다.

## 기술 스택

| 영역 | 기술 |
| --- | --- |
| Backend | FastAPI, SQLAlchemy 2.0, PostgreSQL |
| Frontend | SvelteKit 5, Svelte 5, Tailwind CSS v4 |
| Infrastructure | Docker, Terraform, AWS |

## 빠른 시작

### 필수 요구사항

- Python 3.13+
- Node.js 20+
- Docker & Docker Compose

### 실행

```bash
git clone https://github.com/Sogang-Computer-Club/sogangcomputerclub.org.git
cd sogangcomputerclub.org
cp .env.example .env
docker-compose up -d
```

### 접속 주소

- Frontend: <http://localhost:3000>
- Backend API: <http://localhost:8000>
- API 문서: <http://localhost:8000/docs>

## 문서

자세한 내용은 [개발 문서](docs/)를 참조하세요.

| 문서 | 설명 |
| --- | --- |
| [개발 환경 설정](docs/getting-started.md) | 로컬 개발 환경 구축 |
| [시스템 아키텍처](docs/architecture.md) | 전체 구조 및 설계 원칙 |
| [백엔드 개발](docs/backend.md) | FastAPI, 도메인 구조 |
| [프론트엔드 개발](docs/frontend.md) | SvelteKit, 컴포넌트 패턴 |
| [인프라 설정](docs/infrastructure.md) | Terraform, AWS |
| [배포 가이드](docs/deployment.md) | CI/CD, 프로덕션 배포 |
| [테스트 가이드](docs/testing.md) | 단위/통합/부하 테스트 |
| [문제 해결](docs/troubleshooting.md) | 일반적인 오류와 해결 |
| [기여 치트시트](docs/cheatsheet.md) | 브랜치명, 커밋 형식 빠른 참조 |

## 기여하기

1. Fork → 2. Feature branch 생성 → 3. PR 제출

자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

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

## 라이선스

이 프로젝트는 [MIT License](LICENSE)로 배포됩니다.

---

Made by SGCC

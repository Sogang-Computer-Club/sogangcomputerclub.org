# 오픈소스 프로젝트 개선 구현 계획

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 동아리 회원 대상 오픈소스 프로젝트의 기여 환경 개선 (라이선스, README, 기여 가이드)

**Architecture:** 문서 파일만 변경. LICENSE를 MIT로 교체하고, README를 간소화하며, CONTRIBUTING.md에 신규 기여자 가이드를 추가한다.

**Tech Stack:** Markdown, Git

---

## Task 1: LICENSE 파일을 MIT로 교체

**Files:**

- Replace: `LICENSE`

**Step 1: LICENSE 파일 전체 교체**

```text
MIT License

Copyright (c) 2024 Sogang Computer Club (SGCC)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Step 2: 변경 확인**

Run: `cat LICENSE | head -5`
Expected: "MIT License" 및 "Copyright (c) 2024 Sogang Computer Club"

**Step 3: Commit**

```bash
git add LICENSE
git commit -m "license: CC0에서 MIT 라이선스로 변경"
```

---

## Task 2: README.md 간소화

**Files:**

- Replace: `README.md`

**Step 1: README.md 전체 교체**

```markdown
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
```

**Step 2: 줄 수 확인**

Run: `wc -l README.md`
Expected: ~90줄 (기존 779줄에서 대폭 감소)

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: README 간소화 (779줄 → ~90줄)"
```

---

## Task 3: CONTRIBUTING.md 중복 제거 및 첫 기여자 가이드 추가

**Files:**

- Modify: `CONTRIBUTING.md`

**Step 1: 중복 섹션 제거 (21-23줄)**

21-23줄의 중복된 "### 1. 업스트림과의 동기화를 유지하는 방법" 제거:

```markdown
## 시작하기

### 1. 업스트림과의 동기화를 유지하는 방법

포크된 저장소는 GitHub UI를 통해 수동으로 동기화할 수 있습니다.
```

**Step 2: "처음 기여하시나요?" 섹션 추가**

"## 시작하기" 섹션 바로 앞에 다음 섹션 추가:

```markdown
## 처음 기여하시나요?

### 시작하기 좋은 이슈 찾기

다음 라벨이 붙은 이슈를 찾아보세요:

| 라벨 | 설명 |
| --- | --- |
| `good first issue` | 처음 기여하는 분에게 적합한 이슈 |
| `help wanted` | 도움이 필요한 이슈 |
| `documentation` | 문서 개선 (코드 변경 없이 시작 가능) |

👉 [good first issue 목록 보기](https://github.com/Sogang-Computer-Club/sogangcomputerclub.org/labels/good%20first%20issue)

### 첫 기여 추천 영역

1. **문서 오타 수정** - 가장 쉬운 시작점
2. **테스트 추가** - 기존 코드 이해에 도움
3. **UI 개선** - 프론트엔드 컴포넌트 스타일링
```

**Step 3: 변경 확인**

Run: `grep -n "처음 기여하시나요" CONTRIBUTING.md`
Expected: 해당 섹션이 존재함

**Step 4: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs: CONTRIBUTING.md에 첫 기여자 가이드 추가"
```

---

## Task 4: GitHub Labels 설정 안내 문서 추가

**Files:**

- Create: `docs/github-labels.md`

**Step 1: GitHub Labels 설정 문서 작성**

```markdown
# GitHub Labels 설정

이 문서는 프로젝트에서 사용하는 GitHub 라벨을 설명합니다.

## 필수 라벨

GitHub Repository > Settings > Labels에서 다음 라벨을 추가하세요:

| 라벨 | 색상 | 설명 |
| --- | --- | --- |
| `good first issue` | `#7057ff` | 처음 기여하기 좋은 이슈 |
| `help wanted` | `#008672` | 커뮤니티 도움 필요 |
| `documentation` | `#0075ca` | 문서 관련 |
| `frontend` | `#a2eeef` | 프론트엔드 관련 |
| `backend` | `#d4c5f9` | 백엔드 관련 |
| `infrastructure` | `#fbca04` | 인프라 관련 |

## 라벨 사용 가이드

- **새 이슈 생성 시**: 적절한 영역 라벨 (`frontend`, `backend`, `infrastructure`) 부착
- **신규 기여자용 이슈**: `good first issue` 라벨 추가
- **도움 필요 시**: `help wanted` 라벨 추가
```

**Step 2: Commit**

```bash
git add docs/github-labels.md
git commit -m "docs: GitHub Labels 설정 가이드 추가"
```

---

## Task 5: 최종 확인 및 정리

**Step 1: 변경 파일 확인**

Run: `git log --oneline -4`
Expected: 4개의 커밋 (LICENSE, README, CONTRIBUTING, github-labels)

**Step 2: 전체 변경사항 요약**

```bash
git diff --stat HEAD~4
```

**Step 3: (선택) Squash 커밋으로 정리**

필요시 4개 커밋을 1개로 합칠 수 있음:

```bash
git reset --soft HEAD~4
git commit -m "docs: 오픈소스 프로젝트 개선

- LICENSE: CC0 → MIT 라이선스 변경
- README: 779줄 → ~90줄로 간소화
- CONTRIBUTING: 첫 기여자 가이드 추가
- GitHub Labels 설정 가이드 추가"
```

---

## 수동 작업 (GitHub UI)

구현 완료 후 GitHub Repository Settings에서 수동으로 설정:

1. **Labels 추가**: Settings > Labels에서 Task 4의 라벨들 생성
2. **Description 확인**: "서강대학교 중앙컴퓨터동아리 SGCC 공식 웹사이트"
3. **Topics 추가** (선택): `fastapi`, `sveltekit`, `docker`, `university-club`

# SGCC 웹사이트 프로젝트에 기여하기

SGCC 웹사이트 프로젝트에 기여해 주셔서 감사합니다! 이 문서는 포크 기반 프로젝트에 기여하는 작업 흐름을 설명합니다.

## 레포지토리 구조

- **Upstream**: `Sogang-Computer-Club/sogangcomputerclub.org` (원본 레포지토리)
- **Fork**: `USER_NAME/sogangcomputerclub.org` (개발 레포지토리, USER_NAME에는 당신의 GitHub 사용자 이름이 들어갑니다.)

## 작업 흐름: GitHub Flow

우리는 **GitHub Flow**라는 간단한 브랜치 기반 워크플로우를 사용합니다:

1. `master`는 항상 배포 가능한 상태 유지
2. `master`에서 `feature/`로 시작하는 기능 브랜치 생성
3. 리뷰를 위한 Pull Request 생성
4. 승인 후 `master`에 병합

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

## 시작하기

### 1. 업스트림과의 동기화를 유지하는 방법

포크된 저장소는 GitHub UI를 통해 수동으로 동기화할 수 있습니다.

```bash
# GitHub UI를 통해: Fetch upstream
```

### 2. 기능 브랜치 생성

변경사항이 있다면 그대로 작업하지 말고 항상 새 브랜치를 생성하세요. 브랜치 이름은 `feature/`로 시작하는 것이 좋습니다.

```bash
# 먼저 최신 master와 동기화
git checkout master
git pull origin master

# 기능 브랜치 생성
git checkout -b feature/your-feature-name
```

#### 브랜치 명명 규칙

브랜치 이름은 다음의 가이드라인을 따라 정해주세요.

- `feature/` - 새로운 기능
- `bugfix/` 또는 `fix/` - 버그 수정
- `hotfix/` - 긴급 수정
- `docs/` - 문서 변경
- `refactor/` - 코드 리팩토링
- `test/` - 테스트 추가 또는 변경
- `chore/` - 유지보수 작업

### 2.5 Pre-commit Hooks 설치 (권장)

커밋 전에 자동으로 코드 스타일을 검사하고 수정합니다:

```bash
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

설치 후 `git commit` 시 자동으로:
- 백엔드: Ruff 린트 + 포맷팅
- 프론트엔드: Prettier 포맷팅 + svelte-check
- 커밋 메시지: Conventional Commits 형식 검증

수동으로 전체 파일 검사:
```bash
uv run pre-commit run --all-files
```

### 3. 개발 및 테스트

#### 로컬 검증 스크립트 (권장)

CI와 동일한 검사를 로컬에서 한 번에 실행합니다:

```bash
./scripts/check.sh           # 전체 검사
./scripts/check.sh backend   # 백엔드만
./scripts/check.sh frontend  # 프론트엔드만
```

PR을 올리기 전에 이 스크립트로 미리 검증하면 CI 실패를 방지할 수 있습니다.

#### 개별 실행

```bash
# Backend (Python/FastAPI)
uv run pytest tests/ -v --ignore=tests/integration --ignore=tests/load
uv run ruff check app/

# Frontend (SvelteKit)
cd frontend
npm run check
npm run test
npm run build
```

### 4. 변경사항 커밋

커밋 메시지는 [Conventional Commits](https://www.conventionalcommits.org/) 형식을 따릅니다.

#### 방법 1: 대화형 커밋 (권장)

```bash
cd frontend && npm run cz
```

대화형으로 커밋 유형, 범위, 메시지를 입력할 수 있습니다.

#### 방법 2: 직접 작성

```bash
git add .
git commit -m "feat: add user authentication feature"
```

pre-commit hook이 커밋 메시지 형식을 자동으로 검증합니다.

#### 커밋 메시지 형식

커밋 메시지를 작성할 때는 다음의 가이드라인을 따라 작성해주세요.

- `feat:` - 새로운 기능
- `fix:` - 버그 수정
- `docs:` - 문서 변경
- `refactor:` - 코드 리팩토링
- `test:` - 테스트 변경
- `chore:` - 유지보수

### 5. 포크에 푸시

```bash
git push origin feature/your-feature-name
```

### 6. Pull Request 생성

변경사항을 실제로 반영하기 위해서는 Pull Request를 생성해야 합니다.

#### 포크로 PR (테스트용):
1. GitHub에서 포크로 이동
2. "Pull requests" → "New pull request" 클릭
3. Base: `master` ← Compare: `feature/your-feature-name`
4. 설명 추가 및 제출

`pr-validation.yml` 워크플로우가 자동으로 실행되어 다음을 확인합니다:
- PR 제목 및 설명 검증
- 병합 충돌
- CI 테스트 (`backend-ci.yml` 및 `frontend-ci.yml` 통해)

#### Upstream으로 PR (기여용):
1. 업스트림 레포지토리로 이동: `Sogang-Computer-Club/sogangcomputerclub.org`
2. "Pull requests" → "New pull request" → "compare across forks" 클릭
3. Base: `Sogang-Computer-Club:master` ← Compare: `USER_NAME:feature/your-feature-name`
4. 변경사항을 설명하는 상세한 설명 추가
5. 업스트림 관리자의 리뷰 대기

## CI/CD 워크플로우

### 포크의 자동화된 워크플로우

- **`backend-ci.yml`**: 백엔드 변경 시 Python 테스트 실행
- **`frontend-ci.yml`**: 프론트엔드 변경 시 TypeScript/Svelte 테스트 실행
- **`docker-build.yml`**: 기능 브랜치에 대한 Docker 이미지 빌드
- **`integration-tests.yml`**: 통합 테스트 실행
- **`security-scan.yml`**: 취약점 스캔

- **`pr-validation.yml`**: 병합 전 PR 검증

### 워크플로우 트리거 패턴

대부분의 워크플로우는 다음에서 트리거됩니다:
- `master` 또는 기능 브랜치 (`feature/*`, `bugfix/*` 등)에 푸시
- `master`로의 Pull Request

## 코드 리뷰 프로세스

1. **자체 리뷰**: PR을 생성하기 전에 자신의 코드 확인
2. **자동 검사**: 모든 CI 워크플로우가 통과하는지 확인
3. **동료 리뷰**: 리뷰어의 피드백 반영
4. **승인**: 병합 전 승인 받기
5. **병합**: Squash and merge 또는 merge commit (프로젝트 선호도에 따라)

## 배포

### Production
- 업스트림의 `master` 브랜치에 푸시 시 트리거
- 업스트림 관리자만 프로덕션에 배포 가능

## 문제 해결

### 동기화 충돌

자동 동기화가 실패한 경우:

```bash
# 수동 동기화
git checkout master
git fetch upstream
git merge upstream/master
# 충돌이 있는 경우 해결
git push origin master
```

### CI 검사 실패

1. GitHub Actions에서 워크플로우 로그 확인
2. 로컬에서 테스트를 실행하여 문제 재현
3. 문제를 수정하고 다시 푸시

### PR의 병합 충돌

```bash
# 최신 master로 기능 브랜치 업데이트
git checkout feature/your-feature-name
git fetch origin
git merge origin/master
# 충돌 해결
git push origin feature/your-feature-name
```

## 질문이 있으신가요?

질문이 있으시면 이슈를 생성하거나 관리자에게 문의하세요.

## 라이선스

기여함으로써 당신의 기여에 프로젝트와 동일한 라이선스가 적용됨에 동의합니다.

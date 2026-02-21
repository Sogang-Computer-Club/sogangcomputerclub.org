# 개발자 경험(DX) 개선 구현 계획

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 동아리 회원들이 기여 시 개발에만 전념할 수 있도록 자동화와 가이드를 구현한다.

**Architecture:** Pre-commit hooks로 커밋 전 자동 검증, Commitizen으로 커밋 메시지 가이드, CI 워크플로우에서 친절한 실패 코멘트 제공, 로컬 검증 스크립트로 CI 환경 재현.

**Tech Stack:** pre-commit, Ruff, Prettier, ESLint, Commitizen, Commitlint, GitHub Actions

---

## Phase 1: Pre-commit Hooks

### Task 1.1: pre-commit 의존성 추가

**Files:**
- Modify: `pyproject.toml:38-47`

**Step 1: pyproject.toml에 pre-commit 추가**

`pyproject.toml`의 `[dependency-groups]` dev 섹션에 pre-commit 추가:

```toml
[dependency-groups]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=4.0.0",
    "httpx>=0.27.0",
    "locust>=2.32.0",
    "aiosqlite>=0.20.0",
    "ruff>=0.4.0",
    "pre-commit>=3.6.0",
]
```

**Step 2: 의존성 설치 확인**

Run: `uv sync`
Expected: 성공적으로 설치, pre-commit이 .venv에 포함

**Step 3: pre-commit 버전 확인**

Run: `uv run pre-commit --version`
Expected: `pre-commit X.X.X` 출력

---

### Task 1.2: .pre-commit-config.yaml 생성

**Files:**
- Create: `.pre-commit-config.yaml`

**Step 1: 설정 파일 생성**

`.pre-commit-config.yaml`:

```yaml
# Pre-commit hooks 설정
# 설치: uv sync && pre-commit install && pre-commit install --hook-type commit-msg
# 수동 실행: pre-commit run --all-files

repos:
  # 백엔드: Ruff 린트 + 포맷팅
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
        files: ^(app|tests)/
      - id: ruff-format
        files: ^(app|tests)/

  # 프론트엔드: Prettier + ESLint + svelte-check
  - repo: local
    hooks:
      - id: prettier
        name: prettier (frontend)
        entry: bash -c 'cd frontend && npx prettier --write --ignore-unknown "$@"' --
        language: system
        files: ^frontend/.*\.(ts|js|svelte|css|json|html)$

      - id: svelte-check
        name: svelte-check (frontend)
        entry: bash -c 'cd frontend && npm run check'
        language: system
        files: ^frontend/.*\.(ts|svelte)$
        pass_filenames: false

  # 커밋 메시지 검증 (Conventional Commits)
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.6.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert]
```

**Step 2: 설정 파일 문법 검증**

Run: `uv run pre-commit validate-config`
Expected: 에러 없이 종료

---

### Task 1.3: pre-commit hooks 설치 및 테스트

**Files:**
- None (git hooks 설치)

**Step 1: Git hooks 설치**

Run: `uv run pre-commit install && uv run pre-commit install --hook-type commit-msg`
Expected: `pre-commit installed at .git/hooks/pre-commit` 및 `pre-commit installed at .git/hooks/commit-msg`

**Step 2: 전체 파일에 대해 hooks 실행**

Run: `uv run pre-commit run --all-files`
Expected: 모든 hook이 Passed 또는 자동 수정 후 Passed (일부 파일 수정될 수 있음)

**Step 3: 커밋 메시지 검증 테스트 (실패 케이스)**

Run: `echo "bad commit message" | uv run pre-commit run conventional-pre-commit --hook-stage commit-msg --commit-msg-filename /dev/stdin`
Expected: Failed (Conventional Commits 형식이 아니므로)

**Step 4: 커밋 메시지 검증 테스트 (성공 케이스)**

Run: `echo "feat: add new feature" | uv run pre-commit run conventional-pre-commit --hook-stage commit-msg --commit-msg-filename /dev/stdin`
Expected: Passed

---

### Task 1.4: CONTRIBUTING.md 업데이트

**Files:**
- Modify: `CONTRIBUTING.md`

**Step 1: pre-commit 설치 안내 추가**

`CONTRIBUTING.md`의 "3. 개발 및 테스트" 섹션 앞에 다음 내용 추가:

```markdown
### 2.5 Pre-commit Hooks 설치 (권장)

커밋 전에 자동으로 코드 스타일을 검사하고 수정합니다:

\`\`\`bash
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
\`\`\`

설치 후 `git commit` 시 자동으로:
- 백엔드: Ruff 린트 + 포맷팅
- 프론트엔드: Prettier 포맷팅 + svelte-check
- 커밋 메시지: Conventional Commits 형식 검증

수동으로 전체 파일 검사:
\`\`\`bash
uv run pre-commit run --all-files
\`\`\`
```

---

### Task 1.5: Phase 1 커밋

**Step 1: 변경 파일 확인**

Run: `git status`
Expected: pyproject.toml, .pre-commit-config.yaml, CONTRIBUTING.md 변경/추가

**Step 2: 커밋**

```bash
git add pyproject.toml .pre-commit-config.yaml CONTRIBUTING.md
git commit -m "feat: pre-commit hooks 설정 추가

- Ruff 린트/포맷팅 (백엔드)
- Prettier + svelte-check (프론트엔드)
- Conventional Commits 검증"
```

---

## Phase 2: Commitizen + 커밋 메시지 검증

### Task 2.1: Commitizen 의존성 추가

**Files:**
- Modify: `frontend/package.json`

**Step 1: package.json에 commitizen 관련 패키지 추가**

`frontend/package.json`의 devDependencies에 추가:

```json
"devDependencies": {
    // ... 기존 항목들 ...
    "commitizen": "^4.3.0",
    "cz-customizable": "^7.2.1",
    "@commitlint/cli": "^19.0.0",
    "@commitlint/config-conventional": "^19.0.0"
}
```

**Step 2: scripts에 cz 명령어 추가**

```json
"scripts": {
    // ... 기존 항목들 ...
    "cz": "cz"
}
```

**Step 3: 의존성 설치**

Run: `cd frontend && npm install`
Expected: 성공적으로 설치

---

### Task 2.2: Commitizen 설정 파일 생성

**Files:**
- Create: `.cz-config.js` (루트)

**Step 1: cz-customizable 설정 파일 생성**

`.cz-config.js`:

```javascript
// Commitizen 설정 (한글 프롬프트)
// 사용법: cd frontend && npm run cz

module.exports = {
  types: [
    { value: 'feat', name: 'feat:     새로운 기능' },
    { value: 'fix', name: 'fix:      버그 수정' },
    { value: 'docs', name: 'docs:     문서 변경' },
    { value: 'style', name: 'style:    코드 포맷팅 (기능 변경 없음)' },
    { value: 'refactor', name: 'refactor: 코드 리팩토링' },
    { value: 'perf', name: 'perf:     성능 개선' },
    { value: 'test', name: 'test:     테스트 추가/수정' },
    { value: 'build', name: 'build:    빌드 시스템 변경' },
    { value: 'ci', name: 'ci:       CI 설정 변경' },
    { value: 'chore', name: 'chore:    기타 유지보수' },
    { value: 'revert', name: 'revert:   커밋 되돌리기' },
  ],

  scopes: [
    { name: 'frontend' },
    { name: 'backend' },
    { name: 'infra' },
    { name: 'docs' },
    { name: 'ci' },
  ],

  messages: {
    type: '변경 유형 선택:',
    scope: '변경 범위 (선택사항, Enter로 건너뛰기):',
    subject: '짧은 설명 (필수):\n',
    body: '자세한 설명 (선택사항, Enter로 건너뛰기):\n',
    breaking: '주요 변경사항 (BREAKING CHANGE) 설명 (선택사항):\n',
    footer: '관련 이슈 번호 (예: #123, 선택사항):\n',
    confirmCommit: '위 내용으로 커밋하시겠습니까?',
  },

  allowCustomScopes: true,
  allowBreakingChanges: ['feat', 'fix'],
  skipQuestions: ['body', 'breaking', 'footer'],
  subjectLimit: 100,
};
```

---

### Task 2.3: Commitlint 설정 파일 생성

**Files:**
- Create: `commitlint.config.js` (루트)

**Step 1: commitlint 설정 파일 생성**

`commitlint.config.js`:

```javascript
// Commitlint 설정
// Conventional Commits 형식 검증

module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // 허용되는 타입
    'type-enum': [
      2,
      'always',
      [
        'feat',
        'fix',
        'docs',
        'style',
        'refactor',
        'perf',
        'test',
        'build',
        'ci',
        'chore',
        'revert',
      ],
    ],
    // 한글 subject 허용 (case 검사 비활성화)
    'subject-case': [0],
    // subject 길이 제한
    'subject-max-length': [2, 'always', 100],
  },
};
```

---

### Task 2.4: package.json에 commitizen config 추가

**Files:**
- Modify: `frontend/package.json`

**Step 1: config.commitizen 섹션 추가**

`frontend/package.json`에 추가:

```json
{
  // ... 기존 내용 ...
  "config": {
    "commitizen": {
      "path": "cz-customizable"
    },
    "cz-customizable": {
      "config": "../.cz-config.js"
    }
  }
}
```

---

### Task 2.5: Commitizen 테스트

**Step 1: cz 명령어 테스트**

Run: `cd frontend && npm run cz -- --dry-run`
Expected: 대화형 프롬프트가 한글로 표시됨

**Step 2: commitlint 테스트 (실패 케이스)**

Run: `echo "bad message" | cd frontend && npx commitlint`
Expected: 에러 출력 (형식 오류)

**Step 3: commitlint 테스트 (성공 케이스)**

Run: `echo "feat: add feature" | cd frontend && npx commitlint`
Expected: 에러 없이 종료

---

### Task 2.6: CONTRIBUTING.md 업데이트

**Files:**
- Modify: `CONTRIBUTING.md`

**Step 1: Commitizen 사용법 추가**

`CONTRIBUTING.md`의 "4. 변경사항 커밋" 섹션 수정:

```markdown
### 4. 변경사항 커밋

커밋 메시지는 [Conventional Commits](https://www.conventionalcommits.org/) 형식을 따릅니다.

#### 방법 1: 대화형 커밋 (권장)

```bash
cd frontend && npm run cz
```

대화형으로 커밋 유형, 범위, 메시지를 입력할 수 있습니다.

#### 방법 2: 직접 작성

```bash
git commit -m "feat: add user authentication feature"
```

pre-commit hook이 커밋 메시지 형식을 자동으로 검증합니다.
```

---

### Task 2.7: Phase 2 커밋

**Step 1: 변경 파일 확인**

Run: `git status`
Expected: frontend/package.json, .cz-config.js, commitlint.config.js, CONTRIBUTING.md 변경/추가

**Step 2: 커밋**

```bash
git add frontend/package.json .cz-config.js commitlint.config.js CONTRIBUTING.md
git commit -m "feat: Commitizen 대화형 커밋 도구 추가

- cz-customizable로 한글 프롬프트 지원
- commitlint로 커밋 메시지 형식 검증
- CONTRIBUTING.md에 사용법 추가"
```

---

## Phase 3: CI 실패 시 친절한 코멘트

### Task 3.1: backend-ci.yml 수정

**Files:**
- Modify: `.github/workflows/backend-ci.yml`

**Step 1: 린트 실패 시 친절한 코멘트 추가**

`.github/workflows/backend-ci.yml`의 lint job 수정:

```yaml
  lint:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install dependencies
        run: uv sync

      - name: Lint with ruff
        id: lint
        run: |
          uv run ruff check app/ tests/ 2>&1 | tee lint_output.txt
          exit ${PIPESTATUS[0]}
        continue-on-error: true

      - name: Check formatting with ruff
        id: format
        run: |
          uv run ruff format --check app/ tests/ 2>&1 | tee format_output.txt
          exit ${PIPESTATUS[0]}
        continue-on-error: true

      - name: Comment on PR if lint failed
        if: steps.lint.outcome == 'failure' && github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const output = fs.readFileSync('lint_output.txt', 'utf8');
            const body = `[실패] 백엔드 린트 검사 실패

\`\`\`
${output.slice(0, 3000)}
\`\`\`

**해결 방법:**
\`\`\`bash
uv run ruff check app/ --fix
\`\`\`

**팁:** \`pre-commit install\`을 실행하면 커밋 전에 자동으로 검사됩니다.`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });

      - name: Comment on PR if format failed
        if: steps.format.outcome == 'failure' && github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const output = fs.readFileSync('format_output.txt', 'utf8');
            const body = `[실패] 백엔드 포맷 검사 실패

\`\`\`
${output.slice(0, 3000)}
\`\`\`

**해결 방법:**
\`\`\`bash
uv run ruff format app/
\`\`\`

**팁:** \`pre-commit install\`을 실행하면 커밋 전에 자동으로 포맷팅됩니다.`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });

      - name: Fail if lint or format failed
        if: steps.lint.outcome == 'failure' || steps.format.outcome == 'failure'
        run: exit 1
```

---

### Task 3.2: frontend-ci.yml 수정

**Files:**
- Modify: `.github/workflows/frontend-ci.yml`

**Step 1: 타입 체크/테스트 실패 시 친절한 코멘트 추가**

`.github/workflows/frontend-ci.yml` 수정:

```yaml
name: Frontend CI

on:
  push:
    branches: [main, master, "feature/frontend-*", "feature/CI-CD"]
    paths:
      - "frontend/**"
      - ".github/workflows/frontend-ci.yml"
  pull_request:
    branches: [main, master]
    paths:
      - "frontend/**"

jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./frontend

    strategy:
      matrix:
        node-version: [20.x]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Run type checking
        id: typecheck
        run: |
          npm run check 2>&1 | tee typecheck_output.txt
          exit ${PIPESTATUS[0]}
        continue-on-error: true

      - name: Run tests
        id: test
        run: |
          npm run test 2>&1 | tee test_output.txt
          exit ${PIPESTATUS[0]}
        continue-on-error: true

      - name: Build project
        id: build
        run: npm run build
        continue-on-error: true

      - name: Comment on PR if typecheck failed
        if: steps.typecheck.outcome == 'failure' && github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const output = fs.readFileSync('frontend/typecheck_output.txt', 'utf8');
            const body = `[실패] 프론트엔드 타입 체크 실패

\`\`\`
${output.slice(0, 3000)}
\`\`\`

**해결 방법:**
\`\`\`bash
cd frontend && npm run check
\`\`\`

에러 메시지를 확인하고 타입 오류를 수정하세요.`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });

      - name: Comment on PR if test failed
        if: steps.test.outcome == 'failure' && github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const output = fs.readFileSync('frontend/test_output.txt', 'utf8');
            const body = `[실패] 프론트엔드 테스트 실패

\`\`\`
${output.slice(0, 3000)}
\`\`\`

**해결 방법:**
\`\`\`bash
cd frontend && npm run test
\`\`\`

실패한 테스트를 확인하고 수정하세요.`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });

      - name: Fail if any step failed
        if: steps.typecheck.outcome == 'failure' || steps.test.outcome == 'failure' || steps.build.outcome == 'failure'
        run: exit 1

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        if: steps.build.outcome == 'success'
        with:
          name: frontend-build
          path: frontend/build/
          retention-days: 7
```

---

### Task 3.3: pr-validation.yml 수정

**Files:**
- Modify: `.github/workflows/pr-validation.yml`

**Step 1: 브랜치명/PR 형식 오류 시 친절한 코멘트 개선**

`.github/workflows/pr-validation.yml`의 branch name validation 수정:

```yaml
      - name: Validate branch name
        id: branch
        env:
          BRANCH_NAME: ${{ github.head_ref }}
        run: |
          if [[ ! "$BRANCH_NAME" =~ ^(feature|bugfix|hotfix|fix|docs|refactor|test|chore)/.+ ]]; then
            echo "valid=false" >> $GITHUB_OUTPUT
            echo "branch=$BRANCH_NAME" >> $GITHUB_OUTPUT
          else
            echo "valid=true" >> $GITHUB_OUTPUT
          fi

      - name: Comment on invalid branch name
        if: steps.branch.outputs.valid == 'false'
        uses: actions/github-script@v7
        with:
          script: |
            const branch = '${{ steps.branch.outputs.branch }}';
            const body = `[실패] 브랜치 이름이 규칙에 맞지 않습니다

현재 브랜치: \`${branch}\`

**올바른 형식:**
- \`feature/기능명\` - 새로운 기능
- \`fix/버그명\` - 버그 수정
- \`docs/문서명\` - 문서 변경
- \`refactor/대상\` - 리팩토링
- \`test/테스트명\` - 테스트 추가
- \`chore/작업명\` - 기타 유지보수

**예시:** \`feature/login-validation\`, \`fix/api-timeout\`

**해결 방법:**
\`\`\`bash
git branch -m ${branch} feature/적절한-이름
git push origin -u feature/적절한-이름
\`\`\``;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });

      - name: Fail if branch name invalid
        if: steps.branch.outputs.valid == 'false'
        run: exit 1
```

---

### Task 3.4: Phase 3 커밋

**Step 1: 변경 파일 확인**

Run: `git status`
Expected: .github/workflows/backend-ci.yml, frontend-ci.yml, pr-validation.yml 변경

**Step 2: 커밋**

```bash
git add .github/workflows/backend-ci.yml .github/workflows/frontend-ci.yml .github/workflows/pr-validation.yml
git commit -m "feat: CI 실패 시 친절한 코멘트 추가

- backend-ci: 린트/포맷 실패 시 해결 방법 안내
- frontend-ci: 타입체크/테스트 실패 시 해결 방법 안내
- pr-validation: 브랜치명 오류 시 올바른 형식 안내"
```

---

## Phase 4: 로컬 검증 스크립트

### Task 4.1: scripts/check.sh 생성

**Files:**
- Create: `scripts/check.sh`

**Step 1: 스크립트 생성**

`scripts/check.sh`:

```bash
#!/bin/bash
# 로컬 검증 스크립트 - CI와 동일한 검사를 로컬에서 실행
# 사용법: ./scripts/check.sh [backend|frontend|all]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 카운터
TOTAL=0
PASSED=0
FAILED=0
FAILED_CHECKS=()

# 체크 실행 함수
run_check() {
    local name=$1
    local cmd=$2
    ((TOTAL++))

    printf "[%d] %s... " "$TOTAL" "$name"

    # 임시 파일에 출력 저장
    local output_file=$(mktemp)

    if eval "$cmd" > "$output_file" 2>&1; then
        echo -e "${GREEN}OK${NC}"
        ((PASSED++))
        rm -f "$output_file"
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        ((FAILED++))
        FAILED_CHECKS+=("$name")
        echo -e "${YELLOW}--- 에러 출력 ---${NC}"
        cat "$output_file"
        echo -e "${YELLOW}--- 에러 끝 ---${NC}"
        rm -f "$output_file"
        return 1
    fi
}

# 백엔드 검사
run_backend_checks() {
    echo ""
    echo "=== 백엔드 검사 ==="

    run_check "백엔드 린트 검사 (ruff check)" "uv run ruff check app/ tests/" || true
    run_check "백엔드 포맷 검사 (ruff format)" "uv run ruff format --check app/ tests/" || true
    run_check "백엔드 테스트 (pytest)" "uv run pytest tests/ -v --ignore=tests/integration --ignore=tests/load -q" || true
}

# 프론트엔드 검사
run_frontend_checks() {
    echo ""
    echo "=== 프론트엔드 검사 ==="

    run_check "프론트엔드 타입 체크 (svelte-check)" "cd frontend && npm run check" || true
    run_check "프론트엔드 테스트 (vitest)" "cd frontend && npm run test" || true
    run_check "프론트엔드 빌드" "cd frontend && npm run build" || true
}

# 결과 출력
print_summary() {
    echo ""
    echo "========================================"
    echo "결과: ${PASSED}/${TOTAL} 통과"

    if [ $FAILED -gt 0 ]; then
        echo ""
        echo -e "${RED}실패한 검사:${NC}"
        for check in "${FAILED_CHECKS[@]}"; do
            echo "  - $check"
        done
        echo ""
        echo "위 오류를 수정 후 다시 실행하세요."
        exit 1
    else
        echo ""
        echo -e "${GREEN}모든 검사를 통과했습니다.${NC}"
        exit 0
    fi
}

# 메인 로직
case "${1:-all}" in
    backend)
        run_backend_checks
        ;;
    frontend)
        run_frontend_checks
        ;;
    all|"")
        run_backend_checks
        run_frontend_checks
        ;;
    *)
        echo "사용법: $0 [backend|frontend|all]"
        echo ""
        echo "  backend   - 백엔드 검사만 실행"
        echo "  frontend  - 프론트엔드 검사만 실행"
        echo "  all       - 전체 검사 실행 (기본값)"
        exit 1
        ;;
esac

print_summary
```

**Step 2: 실행 권한 부여**

Run: `chmod +x scripts/check.sh`

**Step 3: 스크립트 테스트**

Run: `./scripts/check.sh`
Expected: 각 검사 결과가 OK 또는 FAIL로 표시되고 요약 출력

---

### Task 4.2: CONTRIBUTING.md 업데이트

**Files:**
- Modify: `CONTRIBUTING.md`

**Step 1: 로컬 검증 스크립트 안내 추가**

`CONTRIBUTING.md`의 "3. 개발 및 테스트" 섹션 수정:

```markdown
### 3. 개발 및 테스트

#### 로컬 검증 스크립트 (권장)

CI와 동일한 검사를 로컬에서 한 번에 실행합니다:

\`\`\`bash
./scripts/check.sh           # 전체 검사
./scripts/check.sh backend   # 백엔드만
./scripts/check.sh frontend  # 프론트엔드만
\`\`\`

PR을 올리기 전에 이 스크립트로 미리 검증하면 CI 실패를 방지할 수 있습니다.

#### 개별 실행

\`\`\`bash
# Backend (Python/FastAPI)
uv run pytest tests/ -v --ignore=tests/integration --ignore=tests/load
uv run ruff check app/

# Frontend (SvelteKit)
cd frontend
npm run check
npm run test
npm run build
\`\`\`
```

---

### Task 4.3: Phase 4 커밋

**Step 1: 변경 파일 확인**

Run: `git status`
Expected: scripts/check.sh, CONTRIBUTING.md 변경/추가

**Step 2: 커밋**

```bash
git add scripts/check.sh CONTRIBUTING.md
git commit -m "feat: 로컬 검증 스크립트 추가

- scripts/check.sh로 CI와 동일한 검사 로컬 실행
- backend, frontend, all 옵션 지원
- 실패 시 에러 내용 출력"
```

---

## Phase 5: 빠른 참조 치트시트

### Task 5.1: docs/cheatsheet.md 생성

**Files:**
- Create: `docs/cheatsheet.md`

**Step 1: 치트시트 생성**

`docs/cheatsheet.md`:

```markdown
# 기여 치트시트

빠른 참조용 한 페이지 가이드입니다.

## 브랜치 이름

| Prefix | 용도 | 예시 |
|--------|------|------|
| `feature/` | 새 기능 | `feature/login-form` |
| `fix/` | 버그 수정 | `fix/api-timeout` |
| `docs/` | 문서 변경 | `docs/readme-update` |
| `refactor/` | 리팩토링 | `refactor/user-service` |
| `test/` | 테스트 | `test/auth-unit-tests` |
| `chore/` | 유지보수 | `chore/update-deps` |

## 커밋 메시지

| Type | 설명 | 예시 |
|------|------|------|
| `feat:` | 새 기능 | `feat: 로그인 폼 추가` |
| `fix:` | 버그 수정 | `fix: API 타임아웃 해결` |
| `docs:` | 문서 변경 | `docs: README 업데이트` |
| `refactor:` | 리팩토링 | `refactor: 유저 서비스 분리` |
| `test:` | 테스트 | `test: 인증 테스트 추가` |
| `chore:` | 기타 | `chore: 의존성 업데이트` |

## 자주 쓰는 명령어

```bash
# 로컬 검증 (CI와 동일)
./scripts/check.sh

# 대화형 커밋
cd frontend && npm run cz

# Pre-commit 전체 실행
uv run pre-commit run --all-files

# 린트 자동 수정
uv run ruff check app/ --fix
uv run ruff format app/
```

## PR 체크리스트

- [ ] 브랜치명이 `feature/`, `fix/` 등으로 시작하는가?
- [ ] `./scripts/check.sh` 통과했는가?
- [ ] 커밋 메시지가 `feat:`, `fix:` 등으로 시작하는가?
- [ ] PR 설명에 변경 내용을 작성했는가?

## 도움이 필요하면

- [CONTRIBUTING.md](../CONTRIBUTING.md) - 상세 기여 가이드
- [개발 환경 설정](./getting-started.md) - 로컬 환경 구축
```

---

### Task 5.2: README.md에 치트시트 링크 추가

**Files:**
- Modify: `README.md`

**Step 1: 문서 테이블에 치트시트 추가**

`README.md`의 문서 테이블에 추가:

```markdown
| [기여 치트시트](docs/cheatsheet.md) | 브랜치명, 커밋 형식 빠른 참조 |
```

---

### Task 5.3: Phase 5 커밋

**Step 1: 변경 파일 확인**

Run: `git status`
Expected: docs/cheatsheet.md, README.md 변경/추가

**Step 2: 커밋**

```bash
git add docs/cheatsheet.md README.md
git commit -m "docs: 기여 치트시트 추가

- 브랜치명, 커밋 메시지 형식 빠른 참조
- 자주 쓰는 명령어 모음
- PR 체크리스트"
```

---

## 최종 검증

### Task 6.1: 전체 동작 테스트

**Step 1: pre-commit 전체 실행**

Run: `uv run pre-commit run --all-files`
Expected: 모든 hook Passed

**Step 2: 로컬 검증 스크립트 실행**

Run: `./scripts/check.sh`
Expected: 모든 검사 통과

**Step 3: 문서 확인**

- `docs/cheatsheet.md` 내용 확인
- `CONTRIBUTING.md` 변경사항 확인
- `README.md` 링크 확인

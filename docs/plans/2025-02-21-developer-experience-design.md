# 개발자 경험(DX) 개선 설계

동아리 회원들이 기여 시 개발에만 전념할 수 있도록 자동화와 가이드를 개선한다.

## 문제 정의

### 현재 상황
1. **CI 실패 시 원인 파악 어려움**
   - GitHub Actions 로그가 길고 어디를 봐야 할지 모름
   - 선배에게 질문하는 것이 부담
   - 로컬과 CI 환경 차이로 재현 어려움
   - 해결 방법을 몰라 PR을 포기하는 경우 발생

2. **코드 스타일/컨벤션 학습 부담**
   - 커밋 메시지 형식 (Conventional Commits)
   - 브랜치 이름 규칙 (feature/, fix/ 등)
   - 코드 포맷팅 (Ruff, ESLint)
   - PR 템플릿 작성법

### 해결 방향
- 자동 수정 가능한 것: 자동으로 처리
- 판단이 필요한 것: 친절한 가이드 제공

## 구현 계획

점진적 도입 방식으로 각 Phase를 완료하고 피드백을 받은 후 다음 단계로 진행한다.

### Phase 1: Pre-commit Hooks (1주)

#### 도구
- **pre-commit 프레임워크**: 백엔드(Python) + 프론트엔드(Node) 모두 하나의 설정 파일로 관리

#### 설정 파일
`.pre-commit-config.yaml`:

```yaml
repos:
  # 백엔드: Ruff 린트 + 포맷팅
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  # 프론트엔드: Prettier + ESLint
  - repo: local
    hooks:
      - id: prettier
        name: prettier
        entry: npx prettier --write
        language: system
        files: ^frontend/.*\.(ts|svelte|css|json)$
      - id: eslint
        name: eslint
        entry: npx eslint --fix
        language: system
        files: ^frontend/.*\.(ts|svelte)$
      - id: svelte-check
        name: svelte-check
        entry: bash -c 'cd frontend && npm run check'
        language: system
        files: ^frontend/.*\.(ts|svelte)$
        pass_filenames: false

  # 커밋 메시지 검증
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v4.1.0
    hooks:
      - id: commitizen
        stages: [commit-msg]
```

#### 포함 Hooks

| Hook | 역할 | 자동 수정 |
|------|------|----------|
| ruff | 백엔드 린트 | O |
| ruff-format | 백엔드 코드 포맷 | O |
| prettier | 프론트엔드 포맷팅 | O |
| eslint | 프론트엔드 린트 | O (--fix) |
| svelte-check | Svelte 타입 체크 | X (검사만) |
| commitizen | 커밋 메시지 검증 | X (검사만) |

#### 설치 방법
```bash
uv sync                # pre-commit이 dev dependency로 포함
pre-commit install     # git hooks 설치
pre-commit install --hook-type commit-msg  # 커밋 메시지 훅
```

#### 실패 시 동작
- 자동 수정 가능: 수정 후 "파일이 수정되었습니다. 다시 스테이징하세요." 안내
- 수정 불가능: 에러 위치 + 해결 방법 출력

### Phase 2: Commitizen + 커밋 메시지 검증 (1주)

#### 도구
- **commitizen (cz-cli)**: 대화형 커밋 메시지 작성
- **cz-customizable**: 한글 프롬프트 지원

#### 워크플로우
```
$ pnpm cz

? 변경 유형 선택:
> feat:     새로운 기능
  fix:      버그 수정
  docs:     문서 변경
  refactor: 코드 리팩토링
  test:     테스트 추가/수정
  chore:    유지보수

? 변경 범위 (선택사항): frontend
? 짧은 설명: 로그인 폼 유효성 검사 추가

커밋 메시지: feat(frontend): 로그인 폼 유효성 검사 추가
```

#### 강제 vs 선택
- `git commit`: commitlint가 형식 검증 (필수, Phase 1에서 설정)
- `pnpm cz`: 대화형 가이드 (선택, 권장)

#### 설정 파일
`commitlint.config.js`:
```javascript
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', [
      'feat', 'fix', 'docs', 'refactor', 'test', 'chore', 'style', 'perf', 'ci', 'build', 'revert'
    ]],
    'subject-case': [0],  // 한글 허용
  }
};
```

### Phase 3: CI 실패 시 친절한 코멘트 (1주)

#### 목표
CI 실패 시 PR에 자동 코멘트: 무엇이 실패했는지 + 어떻게 고치는지 안내

#### 코멘트 예시

린트 실패:
```
[실패] 백엔드 린트 검사 실패

`app/api/users.py:42` 에서 문제가 발견되었습니다:
- F401: `os` 모듈이 import되었지만 사용되지 않음

해결 방법:
uv run ruff check app/ --fix

팁: pre-commit install을 실행하면 커밋 전에 자동으로 검사됩니다.
```

타입 체크 실패:
```
[실패] 프론트엔드 타입 체크 실패

`frontend/src/routes/+page.svelte:15` 에서 타입 오류:
- Type 'string' is not assignable to type 'number'

해결 방법:
cd frontend && npm run check
```

#### 적용 워크플로우
- backend-ci.yml: 린트/테스트 실패
- frontend-ci.yml: 타입체크/테스트 실패
- pr-validation.yml: 브랜치명/PR 형식 오류

### Phase 4: 로컬 검증 스크립트 (3일)

#### 파일
`scripts/check.sh`

#### 사용법
```bash
./scripts/check.sh           # 전체 검사
./scripts/check.sh backend   # 백엔드만
./scripts/check.sh frontend  # 프론트엔드만
```

#### 출력 예시
```
[1/6] 백엔드 린트 검사...        OK
[2/6] 백엔드 포맷 검사...        OK
[3/6] 백엔드 테스트...           OK
[4/6] 프론트엔드 타입 체크...    FAIL
      -> frontend/src/lib/api.ts:23 타입 오류
[5/6] 프론트엔드 린트...         OK
[6/6] 프론트엔드 테스트...       OK

결과: 1개 실패. 위 오류를 수정 후 다시 실행하세요.
```

#### 스크립트 구조
```bash
#!/bin/bash
set -e

run_check() {
    local name=$1
    local cmd=$2
    printf "[%d/%d] %s..." "$current" "$total" "$name"
    if eval "$cmd" > /dev/null 2>&1; then
        echo " OK"
        return 0
    else
        echo " FAIL"
        eval "$cmd"  # 에러 출력
        return 1
    fi
}

# 백엔드 검사
run_check "백엔드 린트 검사" "uv run ruff check app/"
run_check "백엔드 포맷 검사" "uv run ruff format --check app/"
run_check "백엔드 테스트" "uv run pytest tests/ -v --ignore=tests/integration --ignore=tests/load"

# 프론트엔드 검사
run_check "프론트엔드 타입 체크" "cd frontend && npm run check"
run_check "프론트엔드 린트" "cd frontend && npm run lint"
run_check "프론트엔드 테스트" "cd frontend && npm run test"
```

### Phase 5: 빠른 참조 치트시트 (2일)

#### 파일
`docs/cheatsheet.md`

#### 내용
```markdown
# 기여 치트시트

## 브랜치 이름
feature/기능명     # 새 기능
fix/버그명         # 버그 수정
docs/문서명        # 문서 변경
refactor/대상      # 리팩토링

예시: feature/login-validation, fix/api-timeout

## 커밋 메시지
feat: 새로운 기능
fix: 버그 수정
docs: 문서 변경
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 기타 유지보수

예시: feat: 로그인 폼 유효성 검사 추가

## 자주 쓰는 명령어
./scripts/check.sh          # CI와 동일한 검사 실행
pnpm cz                     # 대화형 커밋 메시지 작성
pre-commit run --all-files  # 전체 파일 검사

## PR 체크리스트
[ ] 브랜치명이 규칙을 따르는가?
[ ] ./scripts/check.sh 통과했는가?
[ ] PR 설명에 변경 내용을 작성했는가?
```

#### 특징
- A4 한 장 분량 제한
- 예시 중심
- 복사-붙여넣기 가능한 명령어

## 일정 요약

| Phase | 내용 | 예상 기간 |
|-------|------|----------|
| 1 | Pre-commit hooks | 1주 |
| 2 | Commitizen + 커밋 메시지 검증 | 1주 |
| 3 | CI 친절한 코멘트 | 1주 |
| 4 | 로컬 검증 스크립트 | 3일 |
| 5 | 치트시트 문서 | 2일 |

총 예상 기간: 약 4주

## 성공 지표

- CI 실패 후 포기하는 PR 비율 감소
- 선배에게 컨벤션 관련 질문 빈도 감소
- 첫 기여까지 걸리는 시간 단축

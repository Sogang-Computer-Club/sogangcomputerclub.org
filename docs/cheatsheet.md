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

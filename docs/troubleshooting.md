# 문제 해결

개발 및 운영 중 발생할 수 있는 일반적인 오류와 해결 방법입니다.

## 개발 환경

### Docker 관련

### 컨테이너가 시작되지 않음

`docker compose -f deploy/docker-compose.yml ps`로 상태를 확인하고, `docker compose -f deploy/docker-compose.yml logs backend` 또는 `logs frontend`로 로그를 확인합니다. 해결되지 않으면 `docker compose -f deploy/docker-compose.yml down && docker compose -f deploy/docker-compose.yml up -d`로 컨테이너를 재시작합니다.

### 포트 충돌

"Bind for 0.0.0.0:8000 failed: port is already allocated" 오류가 발생하면 `lsof -i :8000`으로 사용 중인 프로세스를 찾아 종료하거나, `deploy/docker-compose.yml`에서 호스트 포트를 변경합니다 (예: `"8001:8000"`).

### 볼륨 권한 문제

`docker compose -f deploy/docker-compose.yml down -v`로 볼륨을 초기화한 뒤 `docker compose -f deploy/docker-compose.yml up -d`로 재시작합니다.

### Alpine Docker GID 충돌

"addgroup: gid '1000' in use" 오류는 Alpine Linux에서 GID 1000이 이미 사용 중일 때 발생합니다. `addgroup --gid 1000` 대신 `addgroup -S appgroup && adduser -S -G appgroup appuser`처럼 시스템 그룹/사용자 방식을 사용합니다.

---

### 백엔드 (Python/FastAPI)

### 모듈을 찾을 수 없음

"ModuleNotFoundError: No module named 'app'" 오류가 발생하면 `which python`으로 가상환경(.venv/bin/python)을 사용 중인지 확인하고, `uv sync`로 의존성을 재설치합니다.

### 데이터베이스 연결 실패

"sqlalchemy.exc.OperationalError: connection refused" 오류의 원인과 해결 방법:

| 확인 항목 | 방법 |
|-----------|------|
| PostgreSQL 실행 여부 | `docker compose -f deploy/docker-compose.yml ps postgres` |
| 환경변수 | `echo $DATABASE_URL` (예: postgresql+asyncpg://user:pass@localhost:5433/db) |
| 포트 | Docker 내부는 `postgres:5432`, 로컬 개발은 `localhost:5433` |

### 마이그레이션 오류

"Target database is not up to date" 오류가 발생하면 `uv run alembic current`로 현재 버전을 확인합니다. 필요 시 `uv run alembic stamp head`로 버전을 강제 설정한 뒤 `uv run alembic upgrade head`로 마이그레이션을 재적용합니다.

### Rate Limiting 테스트 실패

테스트 시 rate limiting이 비활성화되어 있는지 확인합니다. `tests/conftest.py`의 test_app fixture에서 `app.state.limiter.enabled = False`가 설정되어야 합니다.

---

### 프론트엔드 (SvelteKit)

### 빌드 에러

"Cannot find module '$lib/...'" 오류가 발생하면 `rm -rf node_modules package-lock.json && npm install`로 node_modules를 재설치합니다. TypeScript 캐시 문제라면 `rm -rf .svelte-kit && npm run dev`로 캐시를 초기화합니다.

### Hydration 불일치

"Hydration failed because the initial UI does not match" 오류는 SSR과 CSR 결과가 다를 때 발생합니다. `localStorage` 등 브라우저 전용 API는 `$app/environment`의 `browser` 변수로 감싸서 클라이언트에서만 실행되도록 합니다. `$effect` 블록 안에서 `if (browser)` 조건을 사용합니다.

### Context를 찾을 수 없음

"Function called outside component initialization" 오류는 `getContext()`가 컴포넌트 초기화 외부에서 호출될 때 발생합니다. `getContext()`는 반드시 `<script>` 블록 최상위에서 호출해야 하며, 이벤트 핸들러 등 함수 내부에서 호출하면 안 됩니다.

### API 호출 실패 (CORS)

"Access to fetch blocked by CORS policy" 오류가 발생하면 `vite.config.ts`에서 `/api` 경로에 대한 프록시 설정이 `http://localhost:8000`을 target으로 올바르게 구성되어 있는지 확인합니다.

---

### 테스트

### pytest가 테스트를 찾지 못함

`uv run pytest --collect-only`로 테스트 검색 결과를 확인합니다. 파일명이 `test_*.py` 또는 `*_test.py` 패턴을 따르는지 확인합니다.

### async 테스트 오류

"RuntimeWarning: coroutine was never awaited" 경고는 async 테스트 함수에 `@pytest.mark.asyncio` 데코레이터가 누락되었을 때 발생합니다.

### Vitest 타임아웃

`vitest.config.ts`에서 `test.testTimeout` 값을 늘립니다 (예: 10000으로 설정하면 10초).

---

## 배포 환경

### EC2

### SSH 접속 실패

`chmod 400 ~/.ssh/sgcc-production.pem`으로 키 권한을 확인합니다. `aws ec2 describe-security-groups --group-ids sg-xxx`로 보안 그룹에서 내 IP가 허용되어 있는지, `aws ec2 describe-instance-status --instance-ids i-xxx`로 인스턴스 상태를 확인합니다.

### 디스크 용량 부족

`df -h`로 용량을 확인합니다. `docker system prune -af && docker volume prune -f`로 Docker를 정리하고, `sudo journalctl --vacuum-time=7d`로 오래된 로그를 삭제합니다.

### RDS

### 연결 거부

Security Group에서 EC2 -> RDS 허용 여부, RDS가 Private Subnet에 있는지, VPC 라우팅 테이블을 확인합니다. EC2 내부에서 `nc -zv <rds-endpoint> 5432`로 연결을 테스트합니다.

### 느린 쿼리

`pg_stat_activity`에서 idle이 아닌 쿼리를 duration 기준으로 조회하여 실행 중인 쿼리를 확인합니다. `EXPLAIN ANALYZE`로 인덱스 사용 여부를 확인합니다.

### CI/CD

### GitHub Actions YAML 파싱 오류

GitHub Actions의 `script:` 블록에서 JavaScript 템플릿 리터럴(백틱과 `${}`)은 YAML 파서와 충돌할 수 있습니다. 템플릿 리터럴 대신 `'Hello ' + name + '\n' + '**Bold text**'`처럼 문자열 연결 방식을 사용합니다.

### GitHub Actions 실패

| 증상 | 원인 | 해결 |
|------|------|------|
| "Input required and not supplied: role-to-assume" | Secret 누락 | Repository Settings -> Secrets에서 확인 |
| ECR 로그인 실패 | IAM 역할 권한 부족 | ecr:GetAuthorizationToken, ecr:BatchGetImage, ecr:GetDownloadUrlForLayer 권한 확인 |
| SSH 연결 실패 | 키 또는 네트워크 문제 | `EC2_SSH_KEY` Secret이 올바른 PEM 형식인지, Security Group에서 GitHub Actions IP가 허용되어 있는지 확인 |

### 자동 롤백 후 상태 확인

EC2에 SSH 접속 후 `/opt/sgcc` 디렉토리에서 `docker compose -f deploy/docker-compose.aws.yml ps`로 실행 중인 이미지 태그를 확인하고, `docker compose -f deploy/docker-compose.aws.yml logs --tail 100 backend`로 로그를 확인합니다.

---

## 일반적인 오류 메시지

| 오류 | 원인 | 해결 |
|------|------|------|
| `404 Not Found` | 리소스 없음 | ID 확인 |
| `429 Too Many Requests` | Rate limit 초과 | 잠시 대기 |
| `500 Internal Server Error` | 서버 오류 | 로그 확인 |

---

## 로그 확인 방법

### 로컬 개발

백엔드 로그는 `docker compose -f deploy/docker-compose.yml logs -f backend`, 프론트엔드 로그는 `docker compose -f deploy/docker-compose.yml logs -f frontend`로 확인합니다. 특정 시간 이후의 로그만 보려면 `--since 10m` 옵션을 추가합니다.

### 프로덕션

EC2에서 `docker compose -f deploy/docker-compose.aws.yml logs -f`로 확인합니다. AWS Console의 CloudWatch에서 Log Group `/ecs/sgcc-backend`를 확인할 수도 있습니다.

---

## 도움 요청

문제가 해결되지 않으면:

1. **GitHub Issues**: 버그 리포트 작성
2. **문서 확인**: 관련 가이드 재확인
3. **로그 첨부**: 에러 로그와 재현 단계 포함

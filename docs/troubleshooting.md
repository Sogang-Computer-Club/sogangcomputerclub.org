# 문제 해결

개발 및 운영 중 발생할 수 있는 일반적인 오류와 해결 방법입니다.

## 개발 환경

### Docker 관련

#### 컨테이너가 시작되지 않음

```bash
# 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs backend
docker-compose logs frontend

# 컨테이너 재시작
docker-compose down && docker-compose up -d
```

#### 포트 충돌

```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

```bash
# 사용 중인 프로세스 찾기
lsof -i :8000

# 해당 프로세스 종료 또는 docker-compose.yml에서 포트 변경
ports:
  - "8001:8000"  # 호스트 포트 변경
```

#### 볼륨 권한 문제

```bash
# 볼륨 초기화
docker-compose down -v
docker-compose up -d
```

---

### 백엔드 (Python/FastAPI)

#### 모듈을 찾을 수 없음

```
ModuleNotFoundError: No module named 'app'
```

```bash
# 가상환경 확인
which python  # .venv/bin/python 이어야 함

# 의존성 재설치
uv sync
```

#### 데이터베이스 연결 실패

```
sqlalchemy.exc.OperationalError: connection refused
```

**원인 및 해결:**

1. PostgreSQL이 실행 중인지 확인:
   ```bash
   docker-compose ps postgres
   ```

2. 환경변수 확인:
   ```bash
   echo $DATABASE_URL
   # 예: postgresql+asyncpg://user:pass@localhost:5433/db
   ```

3. 포트 확인 (Docker 내부 vs 외부):
   - Docker 내부: `postgres:5432`
   - 로컬 개발: `localhost:5433`

#### 마이그레이션 오류

```
alembic.util.exc.CommandError: Target database is not up to date
```

```bash
# 현재 버전 확인
uv run alembic current

# 강제로 특정 버전으로 설정
uv run alembic stamp head

# 마이그레이션 재적용
uv run alembic upgrade head
```

#### Rate Limiting 테스트 실패

```python
# tests/conftest.py에서 rate limiting 비활성화 확인
@pytest.fixture
def test_app():
    app.state.limiter.enabled = False
    yield app
```

---

### 프론트엔드 (SvelteKit)

#### 빌드 에러

```
Error: Cannot find module '$lib/...'
```

```bash
# node_modules 재설치
rm -rf node_modules package-lock.json
npm install

# TypeScript 캐시 초기화
rm -rf .svelte-kit
npm run dev
```

#### Hydration 불일치

```
Error: Hydration failed because the initial UI does not match
```

**원인:** SSR과 CSR 결과가 다름

**해결:**
```svelte
<script>
    import { browser } from '$app/environment';

    // 클라이언트에서만 실행
    let data = $state(null);

    $effect(() => {
        if (browser) {
            data = localStorage.getItem('key');
        }
    });
</script>
```

#### Context를 찾을 수 없음

```
Error: Function called outside component initialization
```

**원인:** `getContext()`가 컴포넌트 초기화 외부에서 호출됨

**해결:**
```svelte
<script>
    import { getContext } from 'svelte';

    // ✓ 올바름: 스크립트 최상위에서 호출
    const store = getContext(KEY);

    // ✗ 잘못됨: 함수 내부에서 호출
    function handleClick() {
        const store = getContext(KEY);  // Error!
    }
</script>
```

#### API 호출 실패 (CORS)

```
Access to fetch blocked by CORS policy
```

**개발 환경:** `vite.config.ts` 프록시 확인
```typescript
server: {
    proxy: {
        '/api': {
            target: 'http://localhost:8000',
            rewrite: (path) => path.replace(/^\/api/, '')
        }
    }
}
```

---

### 테스트

#### pytest가 테스트를 찾지 못함

```bash
# 테스트 검색 확인
uv run pytest --collect-only

# 파일명이 test_*.py 또는 *_test.py 인지 확인
```

#### async 테스트 오류

```
RuntimeWarning: coroutine was never awaited
```

```python
import pytest

# pytest.mark.asyncio 데코레이터 필요
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

#### Vitest 타임아웃

```typescript
// vitest.config.ts에서 타임아웃 증가
export default defineConfig({
    test: {
        testTimeout: 10000,  // 10초
    }
});
```

---

## 배포 환경

### EC2

#### SSH 접속 실패

```bash
# 키 권한 확인
chmod 400 ~/.ssh/sgcc-production.pem

# 보안 그룹에서 내 IP 허용 확인
aws ec2 describe-security-groups --group-ids sg-xxx

# 인스턴스 상태 확인
aws ec2 describe-instance-status --instance-ids i-xxx
```

#### 디스크 용량 부족

```bash
# 용량 확인
df -h

# Docker 정리
docker system prune -af
docker volume prune -f

# 오래된 로그 삭제
sudo journalctl --vacuum-time=7d
```

### RDS

#### 연결 거부

1. Security Group 확인 (EC2 → RDS 허용)
2. RDS가 Private Subnet에 있는지 확인
3. VPC 라우팅 테이블 확인

```bash
# EC2 내부에서 테스트
nc -zv <rds-endpoint> 5432
```

#### 느린 쿼리

```sql
-- 실행 중인 쿼리 확인
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- 인덱스 사용 확인
EXPLAIN ANALYZE SELECT * FROM memos WHERE title LIKE '%keyword%';
```

### CI/CD

#### GitHub Actions 실패

1. **Secret 누락:**
   ```
   Error: Input required and not supplied: role-to-assume
   ```
   Repository Settings → Secrets에서 확인

2. **ECR 로그인 실패:**
   ```bash
   # IAM 역할 권한 확인
   # ecr:GetAuthorizationToken
   # ecr:BatchGetImage
   # ecr:GetDownloadUrlForLayer
   ```

3. **SSH 연결 실패:**
   - `EC2_SSH_KEY` Secret이 올바른 PEM 형식인지 확인
   - EC2 Security Group에서 GitHub Actions IP 허용

#### 자동 롤백 후 상태 확인

```bash
ssh ec2-user@<EC2_IP>
cd /opt/sgcc

# 현재 실행 중인 이미지 태그 확인
docker-compose -f docker-compose.aws.yml ps

# 로그 확인
docker-compose -f docker-compose.aws.yml logs --tail 100 backend
```

---

## 일반적인 오류 메시지

| 오류 | 원인 | 해결 |
|------|------|------|
| `401 Unauthorized` | 토큰 만료 또는 누락 | 재로그인 |
| `403 Forbidden` | 권한 없음 | 소유자 확인 |
| `404 Not Found` | 리소스 없음 | ID 확인 |
| `429 Too Many Requests` | Rate limit 초과 | 잠시 대기 |
| `500 Internal Server Error` | 서버 오류 | 로그 확인 |

---

## 로그 확인 방법

### 로컬 개발

```bash
# 백엔드 로그
docker-compose logs -f backend

# 프론트엔드 로그
docker-compose logs -f frontend

# 특정 시간 이후
docker-compose logs --since 10m backend
```

### 프로덕션

```bash
# EC2에서
docker-compose -f docker-compose.aws.yml logs -f

# CloudWatch (AWS Console)
# Log Group: /ecs/sgcc-backend
```

---

## 도움 요청

문제가 해결되지 않으면:

1. **GitHub Issues**: 버그 리포트 작성
2. **문서 확인**: 관련 가이드 재확인
3. **로그 첨부**: 에러 로그와 재현 단계 포함


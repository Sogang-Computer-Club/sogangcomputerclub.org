# API 레퍼런스

REST API 엔드포인트 명세입니다.

## 기본 정보

- **Base URL**: `https://sogangcomputerclub.org/api/v1`
- **인증**: Bearer Token (JWT)
- **Content-Type**: `application/json`

## 인증 (Authentication)

### 회원가입

```http
POST /auth/register
```

**Request Body**
```json
{
  "email": "user@sogang.ac.kr",
  "password": "secure_password_123",
  "name": "홍길동",
  "student_id": "20231234"
}
```

**Response** `201 Created`
```json
{
  "id": 1,
  "email": "user@sogang.ac.kr",
  "name": "홍길동",
  "student_id": "20231234",
  "is_active": true,
  "created_at": "2024-01-15T09:00:00Z"
}
```

**Errors**
| 코드 | 설명 |
|------|------|
| 409 | 이미 존재하는 이메일 또는 학번 |
| 422 | 유효하지 않은 입력값 |

---

### 로그인

```http
POST /auth/login
```

**Request Body**
```json
{
  "email": "user@sogang.ac.kr",
  "password": "secure_password_123"
}
```

**Response** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors**
| 코드 | 설명 |
|------|------|
| 401 | 잘못된 이메일 또는 비밀번호 |
| 403 | 비활성화된 계정 |

---

### 토큰 갱신

```http
POST /auth/refresh
Authorization: Bearer {token}
```

**Response** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### 현재 사용자 조회

```http
GET /auth/me
Authorization: Bearer {token}
```

**Response** `200 OK`
```json
{
  "id": 1,
  "email": "user@sogang.ac.kr",
  "name": "홍길동",
  "student_id": "20231234",
  "is_active": true,
  "created_at": "2024-01-15T09:00:00Z"
}
```

---

## 메모 (Memos)

### 메모 목록 조회

```http
GET /memos?skip=0&limit=100
```

**Query Parameters**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| skip | int | 0 | 건너뛸 항목 수 |
| limit | int | 100 | 최대 반환 항목 수 |

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "title": "첫 번째 메모",
    "content": "메모 내용입니다.",
    "author": "user@sogang.ac.kr",
    "created_at": "2024-01-15T09:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  }
]
```

---

### 메모 검색

```http
GET /memos/search?q=검색어&skip=0&limit=100
```

**Query Parameters**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| q | string | ✓ | 검색어 (1-100자) |
| skip | int | | 건너뛸 항목 수 |
| limit | int | | 최대 반환 항목 수 (1-500) |

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "title": "검색어가 포함된 메모",
    "content": "내용에도 검색어가 있습니다.",
    "author": "user@sogang.ac.kr",
    "created_at": "2024-01-15T09:00:00Z"
  }
]
```

---

### 메모 상세 조회

```http
GET /memos/{memo_id}
```

**Response** `200 OK`
```json
{
  "id": 1,
  "title": "메모 제목",
  "content": "메모 내용입니다.",
  "author": "user@sogang.ac.kr",
  "created_at": "2024-01-15T09:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

**Errors**
| 코드 | 설명 |
|------|------|
| 404 | 메모를 찾을 수 없음 |

---

### 메모 생성 🔒

```http
POST /memos
Authorization: Bearer {token}
```

**Request Body**
```json
{
  "title": "새 메모",
  "content": "메모 내용입니다."
}
```

**Response** `201 Created`
```json
{
  "id": 2,
  "title": "새 메모",
  "content": "메모 내용입니다.",
  "author": "user@sogang.ac.kr",
  "created_at": "2024-01-15T11:00:00Z"
}
```

---

### 메모 수정 🔒

```http
PUT /memos/{memo_id}
Authorization: Bearer {token}
```

**Request Body**
```json
{
  "title": "수정된 제목",
  "content": "수정된 내용"
}
```

**Response** `200 OK`
```json
{
  "id": 1,
  "title": "수정된 제목",
  "content": "수정된 내용",
  "author": "user@sogang.ac.kr",
  "created_at": "2024-01-15T09:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

**Errors**
| 코드 | 설명 |
|------|------|
| 403 | 수정 권한 없음 (본인 메모만 수정 가능) |
| 404 | 메모를 찾을 수 없음 |

---

### 메모 삭제 🔒

```http
DELETE /memos/{memo_id}
Authorization: Bearer {token}
```

**Response** `204 No Content`

**Errors**
| 코드 | 설명 |
|------|------|
| 403 | 삭제 권한 없음 (본인 메모만 삭제 가능) |
| 404 | 메모를 찾을 수 없음 |

---

## 헬스체크 (Health)

### 서비스 상태 확인

```http
GET /health
```

**Response** `200 OK`
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

---

## Rate Limiting

API 요청은 Rate Limiting이 적용됩니다.

| 엔드포인트 | 제한 |
|------------|------|
| 인증 (`/auth/*`) | 5회/분 |
| 검색 (`/memos/search`) | 30회/분 |
| 쓰기 (POST/PUT/DELETE) | 10회/분 |
| 기본 (GET) | 100회/분 |

**Rate Limit 초과 시**
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

---

## 에러 응답

모든 에러는 다음 형식을 따릅니다:

```json
{
  "detail": "에러 메시지"
}
```

### HTTP 상태 코드

| 코드 | 의미 |
|------|------|
| 200 | 성공 |
| 201 | 생성 성공 |
| 204 | 삭제 성공 (응답 본문 없음) |
| 400 | 잘못된 요청 |
| 401 | 인증 필요 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 409 | 충돌 (중복) |
| 422 | 유효성 검사 실패 |
| 429 | 요청 횟수 초과 |
| 500 | 서버 오류 |

---

## 인증 사용 예시

### JavaScript (fetch)

```javascript
// 로그인
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@sogang.ac.kr',
    password: 'password123'
  })
});
const { access_token } = await loginResponse.json();

// 인증이 필요한 API 호출
const memoResponse = await fetch('/api/v1/memos', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    title: '새 메모',
    content: '내용'
  })
});
```

### cURL

```bash
# 로그인
TOKEN=$(curl -s -X POST https://sogangcomputerclub.org/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@sogang.ac.kr","password":"password123"}' \
  | jq -r '.access_token')

# 메모 생성
curl -X POST https://sogangcomputerclub.org/api/v1/memos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"새 메모","content":"내용"}'
```

---

## Swagger UI

개발 환경에서 대화형 API 문서를 사용할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 다음 단계

- [백엔드 개발](./backend.md) - API 구현 방법
- [프론트엔드 개발](./frontend.md) - API 호출 패턴


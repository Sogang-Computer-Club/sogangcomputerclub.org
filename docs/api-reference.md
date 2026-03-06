# API 레퍼런스

REST API 엔드포인트 명세입니다.

## 기본 정보

- **Base URL**: `https://sogangcomputerclub.org/api/v1`
- **Content-Type**: `application/json`

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

### 메모 생성

```http
POST /memos
```

**Request Body**
```json
{
  "title": "새 메모",
  "content": "메모 내용입니다.",
  "author": "홍길동"
}
```

**Response** `201 Created`
```json
{
  "id": 2,
  "title": "새 메모",
  "content": "메모 내용입니다.",
  "author": "홍길동",
  "created_at": "2024-01-15T11:00:00Z"
}
```

---

### 메모 수정

```http
PUT /memos/{memo_id}
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
  "author": "홍길동",
  "created_at": "2024-01-15T09:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

**Errors**
| 코드 | 설명 |
|------|------|
| 404 | 메모를 찾을 수 없음 |

---

### 메모 삭제

```http
DELETE /memos/{memo_id}
```

**Response** `204 No Content`

**Errors**
| 코드 | 설명 |
|------|------|
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
  "timestamp": "2024-01-15T12:00:00Z"
}
```

---

## Rate Limiting

API 요청은 Rate Limiting이 적용됩니다.

| 엔드포인트 | 제한 |
|------------|------|
| 검색 (`/memos/search`) | 60회/분 |
| 쓰기 (POST/PUT/DELETE) | 30회/분 |
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
| 404 | 리소스 없음 |
| 422 | 유효성 검사 실패 |
| 429 | 요청 횟수 초과 |
| 500 | 서버 오류 |

---

## 사용 예시

### JavaScript (fetch)

```javascript
// 메모 생성
const response = await fetch('/api/v1/memos', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: '새 메모',
    content: '내용',
    author: '홍길동'
  })
});
```

### cURL

```bash
# 메모 생성
curl -X POST https://sogangcomputerclub.org/api/v1/memos \
  -H "Content-Type: application/json" \
  -d '{"title":"새 메모","content":"내용","author":"홍길동"}'
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


# 모니터링 스택 문서

이 문서는 sogangcomputerclub.org 프로젝트를 위한 Prometheus 및 Grafana 모니터링 구현에 대해 설명합니다.

## 개요

모니터링 스택은 다음으로 구성됩니다:
- **Prometheus**: 지표 수집 및 저장
- **Grafana**: 지표 시각화 및 대시보드
- **FastAPI Instrumentation**: 애플리케이션 지표 노출

## 아키텍처

```
FastAPI App (/metrics) -> Prometheus (scrapes) -> Grafana (queries) -> User Dashboard
```

## 서비스 및 포트

| 서비스 | 포트 (Host) | 포트 (Container) | 목적 |
|------------|-------------|------------------|----------------------------|
| Prometheus | 9090 | 9090 | 지표 수집 및 쿼리 |
| Grafana | 3001 | 3000 | 대시보드 및 시각화 |
| FastAPI | 8000 | 8000 | 애플리케이션 및 지표 |
| PostgreSQL | 5432 | 5432 | 데이터베이스 |
| Redis | 6381 | 6379 | 캐시 |

**참고**: Redis 포트는 호스트 서비스와의 충돌을 피하기 위해 6380에서 변경되었습니다.

## 모니터링 스택 접속

### Prometheus
- URL: http://localhost:9090
- "Targets" 페이지를 사용하여 스크래핑 상태 확인
- 쿼리 예시:
  - `fastapi_requests_total` - 총 요청 수
  - `rate(fastapi_requests_total[5m])` - 초당 요청 비율
  - `histogram_quantile(0.95, rate(fastapi_request_duration_seconds_bucket[5m]))` - 95번째 백분위수 지연 시간

### Grafana
- URL: http://localhost:3001
- 기본 자격 증명: `admin` / `admin`
- 사전 구성된 데이터 소스: Prometheus
- 사전 구성된 대시보드: "FastAPI Application Metrics"

Grafana 자격 증명을 변경하려면 환경 변수를 설정하세요:
```bash
GRAFANA_ADMIN_USER=your_username
GRAFANA_ADMIN_PASSWORD=your_secure_password
```

## 사용 가능한 지표

### 애플리케이션 지표
- `fastapi_requests_total` - 총 요청 카운터 (레이블: method, endpoint, status_code)
- `fastapi_request_duration_seconds` - 요청 지속 시간 히스토그램 (레이블: method, endpoint)
- `memo_total` - 데이터베이스의 총 메모 게이지
- `fastapi_active_connections` - 활성 데이터베이스 연결 게이지

### Python 런타임 지표
- `python_gc_*` - 가비지 컬렉션 통계
- `process_*` - 프로세스 메모리, CPU 사용량

## 대시보드 패널

사전 구성된 FastAPI 대시보드에는 다음이 포함됩니다:
1. **Request Rate** - 시간 경과에 따른 초당 요청 수
2. **Request Duration** - p95 및 p50 지연 시간 백분위수
3. **Total Requests per Second** - 현재 RPS 게이지
4. **Response Status Codes** - 분포 파이 차트
5. **Requests by Endpoint** - API 엔드포인트별 트래픽 분석

## 설정 파일

### Prometheus 설정
- 파일: `prometheus.yml`
- 스크래핑 간격: 15초 (FastAPI의 경우 5초)
- 타겟:
  - prometheus (자체 모니터링)
  - fastapi:8000/metrics

### Grafana 프로비저닝
- 데이터 소스: `grafana/provisioning/datasources/prometheus.yml`
- 대시보드: `grafana/provisioning/dashboards/default.yml`
- 대시보드 JSON: `grafana/provisioning/dashboards/fastapi-dashboard.json`

## Docker Compose 설정

서비스는 `docker-compose.yml` (개발) 및 `docker-compose.prod.yml` (프로덕션) 모두에 정의되어 있습니다.

### 개발
```bash
docker-compose up -d
```

### 프로덕션
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 문제 해결

### FastAPI 지표가 표시되지 않음
1. FastAPI가 실행 중인지 확인: `docker-compose ps`
2. 지표 엔드포인트 확인: `curl http://localhost:8000/metrics`
3. Prometheus 타겟 확인: http://localhost:9090/targets

### Grafana 대시보드가 비어 있음
1. Prometheus 데이터 소스가 연결되었는지 확인 (Configuration -> Data Sources)
2. Prometheus에 데이터가 있는지 확인: http://localhost:9090/graph
3. 대시보드 쿼리가 올바른지 확인

### 포트 충돌
포트 바인딩 오류가 발생하는 경우:
1. 포트를 사용하는 프로세스 확인: `sudo ss -tlnp | grep <port>`
2. 충돌하는 서비스를 중지하거나 docker-compose.yml에서 포트 변경

## 지표 추가하기

FastAPI에 사용자 정의 지표를 추가하려면:

```python
from prometheus_client import Counter, Histogram, Gauge

# 지표 정의
MY_METRIC = Counter('my_metric_total', 'Description', ['label1', 'label2'])

# 코드에서 사용
MY_METRIC.labels(label1='value1', label2='value2').inc()
```

지표는 `/metrics` 엔드포인트에서 자동으로 내보내집니다.

## 헬스 체크

- **FastAPI**: http://localhost:8000/health
- **Prometheus**: http://localhost:9090/-/healthy
- **Grafana**: http://localhost:3001/api/health

## 데이터 영속성

Prometheus와 Grafana는 모두 지속성을 위해 Docker 볼륨을 사용합니다:
- `prometheus_data` - 시계열 지표 데이터 저장
- `grafana_data` - 대시보드, 사용자 및 설정 저장

백업하려면:
```bash
docker run --rm -v sogangcomputercluborg_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz /data
docker run --rm -v sogangcomputercluborg_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz /data
```

## 향후 개선 사항

추가할 수 있는 선택적 익스포터:
- **Redis Exporter**: Redis 캐시 지표 모니터링
- **Postgres Exporter**: PostgreSQL 데이터베이스 지표 모니터링
- **Nginx Exporter**: nginx 웹 서버 지표 모니터링
- **Node Exporter**: 호스트 시스템 지표 모니터링

이들은 prometheus.yml에 사전 구성되어 있지만 아직 배포되지 않았습니다.

# GitHub Labels 설정

이 문서는 프로젝트에서 사용하는 GitHub 라벨을 설명합니다.

## 라벨 목록

GitHub Repository > Settings > Labels에서 다음 라벨을 추가하세요.

### 이슈 타입

| 라벨 | 색상 | 설명 |
| --- | --- | --- |
| `bug` | `#d73a4a` | 버그 리포트 |
| `enhancement` | `#a2eeef` | 새 기능 요청 |

### 영역

| 라벨 | 색상 | 설명 |
| --- | --- | --- |
| `frontend` | `#a2eeef` | 프론트엔드 관련 |
| `backend` | `#d4c5f9` | 백엔드 관련 |
| `infrastructure` | `#fbca04` | 인프라 관련 |
| `ci/cd` | `#0e8a16` | CI/CD 워크플로우 관련 |
| `documentation` | `#0075ca` | 문서 관련 |
| `dependencies` | `#0366d6` | 의존성 업데이트 |
| `security` | `#b60205` | 보안 관련 |
| `configuration` | `#c5def5` | 설정 파일 관련 |

### 기여자용

| 라벨 | 색상 | 설명 |
| --- | --- | --- |
| `good first issue` | `#7057ff` | 처음 기여하기 좋은 이슈 |
| `help wanted` | `#008672` | 커뮤니티 도움 필요 |

### 상태

| 라벨 | 색상 | 설명 |
| --- | --- | --- |
| `duplicate` | `#cfd3d7` | 중복 이슈 |
| `invalid` | `#cfd3d7` | 유효하지 않은 이슈 |
| `wontfix` | `#ffffff` | 수정하지 않을 이슈 |

## 자동 라벨링

PR이 생성되면 변경된 파일에 따라 자동으로 라벨이 부착됩니다.
설정: `.github/labeler.yml`

| 파일 경로 | 자동 부착 라벨 |
| --- | --- |
| `app/**`, `tests/**`, `pyproject.toml` | `backend` |
| `frontend/**` | `frontend` |
| `deploy/docker-compose*.yml`, `**/Dockerfile`, `nginx*.conf` | `infrastructure` |
| `.github/workflows/**` | `ci/cd` |
| `**/*.md`, `docs/**` | `documentation` |
| `package*.json`, `pyproject.toml`, `uv.lock` | `dependencies` |
| `SECURITY.md`, `security-scan.yml` | `security` |
| `*.toml`, `*.yaml`, `*.yml`, `.env.example` | `configuration` |

## 라벨 사용 가이드

- **새 이슈 생성 시**: 적절한 영역 라벨 (`frontend`, `backend`, `infrastructure`) 부착
- **신규 기여자용 이슈**: `good first issue` 라벨 추가
- **도움 필요 시**: `help wanted` 라벨 추가
- **중복 이슈 발견 시**: `duplicate` 라벨 부착 후 원본 이슈 링크

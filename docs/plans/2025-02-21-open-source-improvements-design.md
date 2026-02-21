# 오픈소스 프로젝트 개선 설계

**날짜**: 2025-02-21
**목적**: 동아리 회원 대상 오픈소스 프로젝트로서 기여 환경 개선

## 배경

현재 프로젝트는 오픈소스로 공개되어 있으나 다음 문제점이 있음:
1. CC0 라이선스는 소프트웨어에 적합하지 않음
2. README가 779줄로 과도하게 김
3. 신규 기여자를 위한 가이드 부족

## 설계 결정

### 1. 라이선스 변경: CC0 → MIT

**선택 이유**:
- 가장 단순하고 널리 사용됨
- 상업적 사용, 수정, 배포 모두 허용
- 책임 면제 조항 포함

**변경 파일**:
- `LICENSE` - 전체 교체
- `README.md` - 라이선스 섹션 수정

### 2. README 간소화: 779줄 → ~150줄

**원칙**: README는 프로젝트 소개 + 빠른 시작에 집중

**새 구조**:
```
# sogangcomputerclub.org
- 프로젝트 소개 (1줄)
- 기술 스택 (테이블)
- 빠른 시작 (필수 요구사항, 실행 명령어, 접속 주소)
- 문서 링크 테이블 (/docs로 안내)
- 기여하기 (간단 요약 + CONTRIBUTING.md 링크)
- 개발팀
- 라이선스
```

**삭제/이동되는 섹션**:
| 섹션 | 처리 |
|------|------|
| 아키텍처 다이어그램 | 삭제 (docs/architecture.md에 있음) |
| 로컬 개발 가이드 상세 | 삭제 (docs/getting-started.md에 있음) |
| 테스트 상세 | 삭제 (docs/testing.md에 있음) |
| AWS 인프라 배포 | 삭제 (docs/infrastructure.md에 있음) |
| CI/CD 파이프라인 | 삭제 (docs/deployment.md에 있음) |
| 운영 및 관리 | docs/deployment.md로 이동 |
| 문제 해결 | 삭제 (docs/troubleshooting.md에 있음) |

### 3. 기여 가이드 개선

**CONTRIBUTING.md 변경**:
1. "처음 기여하시나요?" 섹션 추가
2. `good first issue` 라벨 안내
3. 첫 기여 추천 영역 안내
4. 중복 섹션 제거 (23-24줄)

**GitHub Labels 추가** (수동):
| 라벨 | 색상 | 설명 |
|------|------|------|
| `good first issue` | `#7057ff` | 처음 기여하기 좋은 이슈 |
| `help wanted` | `#008672` | 커뮤니티 도움 필요 |
| `documentation` | `#0075ca` | 문서 관련 |
| `frontend` | `#a2eeef` | 프론트엔드 관련 |
| `backend` | `#d4c5f9` | 백엔드 관련 |
| `infrastructure` | `#fbca04` | 인프라 관련 |

## 구현 순서

1. LICENSE 파일 교체 (MIT)
2. README.md 간소화
3. CONTRIBUTING.md 개선
4. GitHub Labels 수동 설정

## 범위 외

- 영문 문서 추가 (동아리 회원 대상이므로 불필요)
- GitHub Topics/Description 영문화
- Apache 2.0 등 다른 라이선스 검토

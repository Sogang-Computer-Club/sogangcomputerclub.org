# SGCC 개발 문서

서강대학교 중앙컴퓨터동아리 웹사이트 개발을 위한 기술 문서입니다.

## 문서 목록

### 시작하기

- [개발 환경 설정](./getting-started.md) - 로컬 개발 환경 구축

### 아키텍처

- [시스템 아키텍처](./architecture.md) - 전체 시스템 구조 및 설계 원칙

### 개발 가이드

- [백엔드 개발](./backend.md) - FastAPI, SQLAlchemy, 도메인 구조
- [프론트엔드 개발](./frontend.md) - SvelteKit, Svelte 5, 컴포넌트 패턴
- [API 레퍼런스](./api-reference.md) - REST API 엔드포인트 명세

### 인프라 및 배포

- [인프라 설정](./infrastructure.md) - Terraform, AWS 리소스
- [배포 가이드](./deployment.md) - CI/CD, 프로덕션 배포

### 품질 관리

- [테스트 가이드](./testing.md) - 단위 테스트, 통합 테스트, 부하 테스트
- [문제 해결](./troubleshooting.md) - 일반적인 오류와 해결 방법

### 운영

- [모니터링](../MONITORING.md) - Prometheus, Grafana 설정
- [메인테이너 가이드](../MAINTAINER_GUIDE.md) - 레포지토리 운영
- [데이터베이스 백업](../backups/README.md) - 백업/복구 절차

기술 스택, 빠른 시작, 기여 방법은 [README.md](../README.md) 참조.
프로젝트 구조는 [아키텍처 문서](./architecture.md) 참조.

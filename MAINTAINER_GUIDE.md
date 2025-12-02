# Maintainer Guide

이 가이드는 기여를 검토하고 병합하는 프로젝트 메인테이너(Maintainer)를 위한 것입니다.

## 목차

- [책임](#책임)
- [PR 리뷰 프로세스](#pr-리뷰-프로세스)
- [병합 가이드라인](#병합-가이드라인)
- [배포 프로세스](#배포-프로세스)
- [자동화된 워크플로우](#자동화된-워크플로우)
- [기여자 관리](#기여자-관리)

---

## 책임

메인테이너로서 당신은 이런 일들을 하게 될 것입니다.

- Pull Request 리뷰 및 병합
- 코드 품질 및 프로젝트 표준 보장하기
- 이슈 및 질문에 응답하기
- 릴리스 관리하기
- CI/CD 파이프라인 유지보수하기
- 새로운 기여자 환영하기

---

## PR 리뷰 프로세스

### 1. 초기 분류

PR이 열리면:

1. **자동화된 검사가 자동으로 실행됩니다:**
   - PR 검증 (제목, 설명, 브랜치 이름)
   - CI 테스트 (백엔드, 프론트엔드, 통합)
   - 보안 스캔
   - 자동 레이블링

2. **확인 사항:**
   - 명확한 PR 설명
   - 연결된 이슈
   - 적절한 레이블
   - CI 검사 통과 여부

### 2. 코드 리뷰

**확인해야 할 사항:**

- **정확성**: 코드가 주장하는 대로 작동하는가??
- **품질**: 코드가 잘 작성되었고 유지보수가 용이한가?
- **테스트**: 적절한 테스트 과정을 통과하였는가?
- **문서화**: 문서가 업데이트되었는가?
- **보안**: 보안 우려 사항이 있는가?
- **성능**: 성능 저하가 있는가?
- **주요 변경 사항**: 필요한 변경이며 문서화되었는가?

**리뷰 체크리스트:**

```markdown
- [ ] 코드가 프로젝트 스타일 가이드를 따름
- [ ] 테스트가 포괄적이며 PR이 해당 테스트를 통과함
- [ ] 문서가 업데이트되었음
- [ ] 보안 취약점이 도입되지 않음
- [ ] 성능 저하 없음
- [ ] 주요 변경 사항이 정당화되고 문서화되었음
- [ ] 커밋 메시지가 명확함
```

### 3. 피드백 제공

**좋은 피드백은:**

- **구체적**: 정확한 줄이나 파일을 지적합니다.
- **건설적**: 비판만 하지 않고 개선 사항을 제안합니다.
- **친절**: 반대편에 사람이 있다는 것을 기억하세요.
- **교육적**: 제안 뒤에 숨겨진 "이유"를 설명합니다.

**피드백 예시:**

```markdown
좋음:
"여기서 Array 대신 Set을 사용하여 O(1) 조회를 고려해보세요.
중복을 확인할 때 성능이 향상될 것입니다."

나쁨:
"이건 느려요."
```

### 4. 변경 요청 또는 승인

- **변경 요청 (Request Changes)**: 병합 전에 반드시 수정해야 하는 문제의 경우
- **코멘트 (Comment)**: 병합을 차단하지 않는 제안의 경우
- **승인 (Approve)**: PR이 모든 기준을 충족할 때

---

## 병합 가이드라인

### 병합 시기

다음 경우에 PR을 병합하세요:

1. 모든 CI 검사 통과
2. 최소 한 명의 메인테이너 승인
3. 해결되지 않은 변경 요청 없음
4. 병합 충돌 없음
5. 기여자가 서명함 (필요한 경우)

### 병합 방법

**Squash and Merge** (기본값, 권장됨)
- 사용: 대부분의 PR
- 기록을 깔끔하게 유지
- 기능당 단일 커밋

```bash
git merge --squash feature-branch
git commit -m "Add feature X"
```

**Merge Commit**
- 사용: 의미 있는 커밋 기록이 있는 대규모 기능
- 모든 커밋 보존

```bash
git merge feature-branch
```

**Rebase and Merge**
- 사용: 깔끔하고 선형적인 기록이 필요한 경우
- 레포지토리(포크 아님)의 PR에만 해당

```bash
git checkout feature-branch
git rebase main
git checkout main
git merge feature-branch
```

### 자동 병합 (Auto-Merge)

동일한 레포지토리(포크 아님)의 PR의 경우,

1. `auto-merge` 레이블 추가하기
2. PR 승인하기
3. 모든 검사가 통과할 때까지 대기하기
4. PR이 자동으로 병합됨

---

## 배포 프로세스

### 릴리스 생성

#### 방법 1: Git 태그 사용

```bash
# 태그 생성 및 푸시
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3
```

#### 방법 2: GitHub Actions 사용

1. Actions → "Create Release"로 이동
2. "Run workflow" 클릭
3. 버전 입력 (예: `v1.2.3`)
4. "Run workflow" 클릭

### 릴리스 버전 관리

[Semantic Versioning](https://semver.org/)을 따릅니다:

- **MAJOR** (v1.0.0 → v2.0.0): 호환되지 않는 API 변경
- **MINOR** (v1.1.0 → v1.2.0): 이전 버전과 호환되는 기능 추가
- **PATCH** (v1.1.1 → v1.1.2): 이전 버전과 호환되는 버그 수정

### 프리 릴리스 (Pre-releases)

알파/베타/RC 릴리스의 경우:

```bash
git tag -a v1.2.3-alpha.1 -m "Alpha release"
git push origin v1.2.3-alpha.1
```

---

## 자동화된 워크플로우

### PR 워크플로우

| 워크플로우 | 트리거 | 목적 |
|----------|---------|---------|
| `pr-validation.yml` | PR 열림/수정됨 | PR 형식 및 내용 검증 |
| `pr-labeler.yml` | PR 열림/업데이트됨 | 파일/크기/유형에 따라 자동 레이블링 |
| `pr-auto-assign.yml` | PR 열림 | 리뷰어 할당, 기여자 환영 |
| `backend-ci.yml` | Push/PR | 백엔드 테스트 실행 |
| `frontend-ci.yml` | Push/PR | 프론트엔드 테스트 실행 |
| `integration-tests.yml` | Push/PR | 통합 테스트 실행 |
| `security-scan.yml` | Push/PR | 보안 스캔 |
| `codeql.yml` | Push/PR/Schedule | GitHub CodeQL 보안 분석 |
| `docker-build.yml` | Push (main) | Docker 이미지 빌드 및 푸시 |

### 유지보수 워크플로우

| 워크플로우 | 트리거 | 목적 |
|----------|---------|---------|
| `stale.yml` | 매일 | 오래된 PR/이슈 표시 및 닫기 |
| `auto-merge.yml` | 리뷰/검사 | 승인된 PR 자동 병합 |
| `release.yml` | 태그 푸시 | 변경 로그와 함께 릴리스 생성 |
| `sync-upstream.yml` | 일정/수동 | 업스트림 저장소와 동기화 |

### 배포 워크플로우

| 워크플로우 | 트리거 | 목적 |
|----------|---------|---------|
| `deploy-production.yml` | 마스터에 푸시 | 프로덕션에 배포 |

---

## 기여자 관리

### 새로운 기여자 환영

누군가 처음으로 기여를 할 때는...

1. 기여에 대해 감사 인사 전하기
2. 더욱 인내심을 갖고 도움을 주기
3. 프로세스 안내하기
4. 향후 기여 장려하기

**응답 템플릿:**

```markdown
환영합니다! 이 프로젝트에 처음 기여해 주셔서 감사합니다!

곧 이 PR을 검토하겠습니다. 그동안 모든 CI 검사가 통과하는지 확인해 주세요.

질문이 있으시면 언제든지 물어보세요!
```

### 어려운 상황 처리

**스팸 PR:**
- 즉시 닫기
- "spam" 레이블 추가
- 필요한 경우 신고

**저품질 PR:**
- 개선이 필요한 부분을 정중하게 설명
- 기여 가이드라인 링크 제공
- 진정한 노력이 보이면 도움 제안

**방치된 PR:**
- 상태를 묻는 코멘트 작성
- 7일 후에도 응답이 없으면 "stale" 레이블 추가
- 총 30일 동안 활동이 없으면 자동 닫기
- 가치 있는 경우 이어받는 것 고려

**기여자 간의 갈등:**
- 중립적이고 전문적인 태도 유지
- 기술적 장점에 집중
- 필요한 경우 행동 강령 참조
- 필요한 경우 최종 결정 내리기

---

## 레이블

### 표준 레이블

**유형 (Type):**
- `type: feature` - 새로운 기능
- `type: bug` - 버그 수정
- `type: documentation` - 문서 변경
- `type: refactor` - 코드 리팩토링
- `type: test` - 테스트 개선
- `type: ci/cd` - CI/CD 변경

**상태 (Status):**
- `status: draft` - 작업 중
- `status: ready` - 리뷰 준비 완료
- `needs review` - 리뷰 대기 중
- `stale` - 비활성 PR/이슈

**크기 (Size):**
- `size/xs` - 아주 작은 변경 (1-10줄)
- `size/s` - 작은 변경 (11-50줄)
- `size/m` - 중간 변경 (51-200줄)
- `size/l` - 큰 변경 (201-500줄)
- `size/xl` - 매우 큰 변경 (500+줄)

**우선순위 (Priority):**
- `priority: high` - 긴급
- `priority: medium` - 보통
- `priority: low` - 있으면 좋음

**기타:**
- `external contribution` - 포크에서 온 기여
- `auto-merge` - 자동 병합 활성화
- `security` - 보안 관련
- `breaking change` - 주요 변경 사항 포함

---

## 모범 사례

### 커뮤니케이션

- 2-3일 이내에 PR에 응답하기
- 명확한 기대치 설정하기
- 일정에 대해 투명하게 공개하기
- 더 많은 시간이 필요한 경우 언급하기

### 코드 품질

- 일관된 표준 적용하기
- 사소한 문제에 너무 엄격하지 않기
- 중요한 것(정확성, 보안, 성능)에 집중하기
- 합리적인 범위 내에서 기여자의 개인 스타일을 허용해주세요

### 의사 결정

- 프로젝트 목표에 기반하여 결정하기
- 이유 설명하기
- 토론에 열린 태도 유지하기
- 친절하게 최종 결정 내리기

---

## 유용한 명령어

### 로컬에서 PR 리뷰하기

```bash
# PR 가져오기
gh pr checkout 123

# 테스트 실행
uv run pytest tests/
cd frontend && npm run test

# 변경 사항 보기
git diff master...HEAD

# 마스터로 복귀
git checkout master
```

### PR 병합하기

```bash
# gh CLI 사용
gh pr merge 123 --squash --delete-branch

# git 사용
git checkout master
git merge --squash pr-branch
git commit
git push origin master
```

### 릴리스 생성하기

```bash
# 태그 생성
git tag -a v1.2.3 -m "Release 1.2.3"
git push origin v1.2.3

# 또는 gh 사용
gh release create v1.2.3 --generate-notes
```

---

## 도움 받기

확신이 서지 않는 경우:

1. 유사한 상황에 대한 기존 PR 확인하기
2. 다른 메인테이너와 논의하기
3. 프로젝트 토론에서 질문하기
4. GitHub 문서 참조하기

기억하세요: 도움을 요청해도 괜찮습니다!

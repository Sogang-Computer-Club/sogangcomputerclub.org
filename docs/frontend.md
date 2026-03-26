# 프론트엔드 개발 가이드

SvelteKit 기반 프론트엔드 개발 방법을 설명합니다.

## 기술 스택

- **SvelteKit 2.0**: 풀스택 프레임워크
- **Svelte 5**: UI 라이브러리 (Runes 사용)
- **TypeScript**: 타입 안전성
- **Tailwind CSS**: 유틸리티 CSS

## 프로젝트 구조

| 경로 | 설명 |
|------|------|
| `routes/` | 페이지 라우트 |
| `routes/+layout.svelte` | 전역 레이아웃 |
| `routes/+page.svelte` | 홈페이지 |
| `routes/about-us/welcome/` | 환영 페이지 |
| `routes/about-us/activity/` | 활동 페이지 |
| `lib/components/` | 재사용 컴포넌트 (Header, Footer, NavigationBar 등) |
| `lib/stores/ui.svelte.ts` | 상태 관리 스토어 |
| `lib/utils/` | 유틸리티 (캘린더 날짜 계산 등) |
| `lib/config/navigation.ts` | 네비게이션 설정 |
| `lib/api.ts` | API 클라이언트 |
| `lib/types/index.ts` | 타입 정의 |
| `hooks.server.ts` | 서버 훅 (보안 헤더) |
| `app.d.ts` | 전역 타입 |

전체 구조는 `frontend/src/` 디렉토리를 참고하세요.

## Svelte 5 패턴

### Runes 사용

Svelte 5에서는 `$state`, `$derived`, `$effect` Runes를 사용하여 반응형 상태를 선언합니다. `$state`로 반응형 변수를 만들고, `$derived`로 파생 값을 자동 재계산하며, `$effect`로 상태 변경 시 사이드 이펙트를 실행합니다.

### 이전 문법 비교

| Svelte 4 | Svelte 5 |
|----------|----------|
| `let count = 0` | `let count = $state(0)` |
| `$: doubled = count * 2` | `let doubled = $derived(count * 2)` |
| `$: { console.log(count) }` | `$effect(() => { console.log(count) })` |
| `on:click={handler}` | `onclick={handler}` |
| `createEventDispatcher()` | 콜백 props |

## 상태 관리

### 클래스 기반 스토어

UI 상태는 `$state` 필드를 가진 클래스로 관리합니다. `UIStore` 클래스가 `sidebarOpen`, `theme` 등의 반응형 상태와 `toggleSidebar()` 같은 메서드를 제공합니다. Context 키는 `Symbol`로 정의하여 타입 안전하게 사용합니다.

See `frontend/src/lib/stores/ui.svelte.ts`

### Context API 사용

레이아웃 컴포넌트(`+layout.svelte`)에서 `setContext`로 스토어 인스턴스를 제공하고, 자식 컴포넌트에서 `getContext`로 꺼내어 사용합니다. `UI_CONTEXT_KEY` 심볼을 키로 사용하여 타입 안전한 Context 접근이 가능합니다.

## 컴포넌트 작성

### 기본 컴포넌트

Svelte 5에서는 `interface Props`로 컴포넌트 속성 타입을 정의하고, `$props()`로 props를 받습니다. 자식 콘텐츠는 `Snippet` 타입의 `children` prop으로 전달하고, `{@render children()}`으로 렌더링합니다.

컴포넌트 props 예시 (Button):

| Prop | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `variant` | `'primary' \| 'secondary'` | `'primary'` | 버튼 스타일 |
| `disabled` | `boolean` | `false` | 비활성화 여부 |
| `onclick` | `() => void` | - | 클릭 핸들러 |
| `children` | `Snippet` | (필수) | 자식 콘텐츠 |

### 사용법

`import Button from '$lib/components/Button.svelte'`로 불러와서 사용합니다. `onclick` 콜백과 slot 대신 `children` Snippet을 통해 자식 콘텐츠를 전달합니다.

## API 호출

### API 클라이언트

API 클라이언트는 SSR과 CSR 환경에 따라 기본 URL을 자동으로 전환합니다. SSR에서는 Docker 내부 통신(`http://backend:8000/v1`), CSR에서는 Vite 프록시(`/api/v1`)를 사용합니다. `getMemos()`, `createMemo()` 등의 함수로 백엔드 API를 호출하며, 응답 실패 시 에러를 throw합니다.

See `frontend/src/lib/api.ts`

### 페이지에서 사용

페이지 컴포넌트에서는 `$state`로 데이터, 로딩, 에러 상태를 관리합니다. `onMount`에서 API를 호출하고, `{#if loading}` / `{:else if error}` / `{:else}` 블록으로 상태별 UI를 분기합니다.

## 라우팅

### 파일 기반 라우팅

SvelteKit은 `routes/` 디렉토리 구조가 곧 URL 경로가 됩니다.

| 파일 경로 | URL |
|-----------|-----|
| `routes/+page.svelte` | `/` |
| `routes/about-us/+page.svelte` | `/about-us` |
| `routes/about-us/welcome/+page.svelte` | `/about-us/welcome` |
| `routes/posts/+page.svelte` | `/posts` |
| `routes/posts/[slug]/+page.svelte` | `/posts/:slug` |

### 동적 라우트

`[slug]` 같은 대괄호 디렉토리로 동적 라우트를 생성합니다. `+page.server.ts`에서 `params.slug`로 URL 파라미터에 접근하여 데이터를 로드하고, `+page.svelte`에서 `data` prop으로 받아 렌더링합니다.

## 테스트

### 컴포넌트 테스트

Vitest + `@testing-library/svelte`를 사용하여 컴포넌트를 테스트합니다. `render`로 컴포넌트를 마운트하고, `getByRole` 등의 쿼리로 요소를 찾으며, `fireEvent`로 사용자 인터랙션을 시뮬레이션합니다.

### Context와 함께 테스트

Context를 사용하는 컴포넌트는 `render`의 `context` 옵션에 `new Map([[UI_CONTEXT_KEY, uiStore]])`를 전달하여 테스트합니다.

### 테스트 실행

- 전체 테스트: `cd frontend && npm run test`
- 감시 모드: `cd frontend && npm run test:watch`

## 스타일링 (Tailwind CSS)

### 기본 사용

Tailwind CSS 유틸리티 클래스를 HTML 요소의 `class` 속성에 직접 작성합니다. 레이아웃(`flex`, `grid`), 간격(`p-4`, `gap-4`), 색상(`bg-gray-100`, `text-gray-900`), 모서리(`rounded-lg`) 등을 조합하여 스타일링합니다.

### 반응형 디자인

Tailwind의 반응형 접두사를 사용하여 화면 크기별 스타일을 적용합니다.

| 접두사 | 최소 너비 |
|--------|-----------|
| `sm:` | 640px |
| `md:` | 768px |
| `lg:` | 1024px |
| `xl:` | 1280px |

예: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`으로 화면 크기에 따라 그리드 열 수를 조정합니다.

## 다음 단계

- [API 레퍼런스](./api-reference.md) - API 명세
- [테스트 가이드](./testing.md) - 테스트 상세

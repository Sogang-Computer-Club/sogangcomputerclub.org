# 프론트엔드 개발 가이드

SvelteKit 기반 프론트엔드 개발 방법을 설명합니다.

## 기술 스택

- **SvelteKit 2.0**: 풀스택 프레임워크
- **Svelte 5**: UI 라이브러리 (Runes 사용)
- **TypeScript**: 타입 안전성
- **Tailwind CSS**: 유틸리티 CSS

## 프로젝트 구조

```
frontend/src/
├── routes/                    # 페이지 라우트
│   ├── +layout.svelte        # 전역 레이아웃
│   ├── +page.svelte          # 홈페이지
│   ├── login/
│   │   └── +page.svelte
│   └── about-us/
│       ├── welcome/
│       │   └── +page.svelte
│       └── activity/
│           └── +page.svelte
├── lib/
│   ├── components/           # 재사용 컴포넌트
│   │   ├── Header.svelte
│   │   ├── Footer.svelte
│   │   ├── NavigationBar.svelte
│   │   └── *.test.ts        # 컴포넌트 테스트
│   ├── stores/               # 상태 관리
│   │   ├── auth.svelte.ts
│   │   └── ui.svelte.ts
│   ├── utils/                # 유틸리티
│   │   └── calculate-calendar-days.ts
│   ├── config/               # 설정
│   │   └── navigation.ts
│   ├── api.ts                # API 클라이언트
│   └── types/                # 타입 정의
│       └── index.ts
├── hooks.server.ts           # 서버 훅 (보안 헤더)
└── app.d.ts                  # 전역 타입
```

## Svelte 5 패턴

### Runes 사용

Svelte 5에서는 `$state`, `$derived`, `$effect`를 사용합니다:

```svelte
<script lang="ts">
    // 반응형 상태
    let count = $state(0);

    // 파생 상태 (자동 재계산)
    let doubled = $derived(count * 2);

    // 사이드 이펙트
    $effect(() => {
        console.log(`Count changed to ${count}`);
    });
</script>

<button onclick={() => count++}>
    Count: {count}, Doubled: {doubled}
</button>
```

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

```typescript
// lib/stores/auth.svelte.ts
import type { User } from '$lib/api';
import { getCurrentUser, refreshToken } from '$lib/api';

export class AuthStore {
    // 반응형 상태
    token = $state<string | null>(null);
    user = $state<User | null>(null);
    isLoading = $state(false);

    // 파생 상태
    isAuthenticated = $derived(!!this.token && !this.isLoading);

    constructor() {
        // 브라우저에서만 localStorage 접근
        if (typeof window !== 'undefined') {
            this.token = localStorage.getItem('access_token');
        }
    }

    setToken(token: string) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('access_token');
    }

    getAuthHeaders(): Record<string, string> {
        return this.token ? { 'Authorization': `Bearer ${this.token}` } : {};
    }
}

// Context 키
export const AUTH_CONTEXT_KEY = Symbol('auth');
```

### Context API 사용

```svelte
<!-- +layout.svelte -->
<script lang="ts">
    import { setContext } from 'svelte';
    import { AuthStore, AUTH_CONTEXT_KEY } from '$lib/stores/auth.svelte';
    import { UIStore, UI_CONTEXT_KEY } from '$lib/stores/ui.svelte';

    // 스토어 인스턴스 생성 및 Context 제공
    const authStore = new AuthStore();
    const uiStore = new UIStore();

    setContext(AUTH_CONTEXT_KEY, authStore);
    setContext(UI_CONTEXT_KEY, uiStore);
</script>

<slot />
```

```svelte
<!-- 자식 컴포넌트에서 사용 -->
<script lang="ts">
    import { getContext } from 'svelte';
    import { AUTH_CONTEXT_KEY, type AuthStore } from '$lib/stores/auth.svelte';

    const authStore = getContext<AuthStore>(AUTH_CONTEXT_KEY);
</script>

{#if authStore.isAuthenticated}
    <p>로그인됨: {authStore.user?.email}</p>
{/if}
```

## 컴포넌트 작성

### 기본 컴포넌트

```svelte
<!-- lib/components/Button.svelte -->
<script lang="ts">
    interface Props {
        variant?: 'primary' | 'secondary';
        disabled?: boolean;
        onclick?: () => void;
        children: import('svelte').Snippet;
    }

    let { variant = 'primary', disabled = false, onclick, children }: Props = $props();
</script>

<button
    class="btn btn-{variant}"
    {disabled}
    {onclick}
>
    {@render children()}
</button>

<style>
    .btn {
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
    }
    .btn-primary {
        background-color: #3b82f6;
        color: white;
    }
    .btn-secondary {
        background-color: #6b7280;
        color: white;
    }
</style>
```

### 사용법

```svelte
<script lang="ts">
    import Button from '$lib/components/Button.svelte';
</script>

<Button variant="primary" onclick={() => console.log('clicked')}>
    클릭하세요
</Button>
```

## API 호출

### API 클라이언트

```typescript
// lib/api.ts
const API_BASE_URL = typeof window === 'undefined'
    ? 'http://backend:8000/v1'   // SSR: Docker 내부 통신
    : '/api/v1';                  // CSR: Vite 프록시

export async function getMemos(): Promise<Memo[]> {
    const response = await fetch(`${API_BASE_URL}/memos/`);
    if (!response.ok) {
        throw new Error('Failed to fetch memos');
    }
    return response.json();
}

export async function createMemo(memo: MemoCreate, token: string): Promise<Memo> {
    const response = await fetch(`${API_BASE_URL}/memos/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(memo),
    });
    if (!response.ok) {
        throw new Error('Failed to create memo');
    }
    return response.json();
}
```

### 페이지에서 사용

```svelte
<!-- routes/memos/+page.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { getContext } from 'svelte';
    import { getMemos, createMemo, type Memo } from '$lib/api';
    import { AUTH_CONTEXT_KEY, type AuthStore } from '$lib/stores/auth.svelte';

    const authStore = getContext<AuthStore>(AUTH_CONTEXT_KEY);

    let memos = $state<Memo[]>([]);
    let loading = $state(true);
    let error = $state<string | null>(null);

    onMount(async () => {
        try {
            memos = await getMemos();
        } catch (e) {
            error = '메모를 불러오는데 실패했습니다';
        } finally {
            loading = false;
        }
    });

    async function handleCreate(title: string, content: string) {
        if (!authStore.token) return;

        const newMemo = await createMemo({ title, content }, authStore.token);
        memos = [newMemo, ...memos];
    }
</script>

{#if loading}
    <p>로딩 중...</p>
{:else if error}
    <p class="error">{error}</p>
{:else}
    <ul>
        {#each memos as memo}
            <li>{memo.title}</li>
        {/each}
    </ul>
{/if}
```

## 라우팅

### 파일 기반 라우팅

```
routes/
├── +page.svelte              → /
├── about-us/
│   ├── +page.svelte          → /about-us
│   └── welcome/
│       └── +page.svelte      → /about-us/welcome
├── posts/
│   ├── +page.svelte          → /posts
│   └── [slug]/
│       └── +page.svelte      → /posts/:slug
```

### 동적 라우트

```svelte
<!-- routes/posts/[slug]/+page.svelte -->
<script lang="ts">
    import type { PageData } from './$types';

    export let data: PageData;
</script>

<h1>{data.post.title}</h1>
```

```typescript
// routes/posts/[slug]/+page.server.ts
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
    const post = await fetchPost(params.slug);
    return { post };
};
```

## 테스트

### 컴포넌트 테스트

```typescript
// lib/components/Button.test.ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import Button from './Button.svelte';

describe('Button', () => {
    it('렌더링된다', () => {
        const { getByRole } = render(Button, {
            props: { children: () => 'Click me' }
        });
        expect(getByRole('button')).toBeInTheDocument();
    });

    it('클릭 시 핸들러가 호출된다', async () => {
        const handleClick = vi.fn();
        const { getByRole } = render(Button, {
            props: { onclick: handleClick, children: () => 'Click me' }
        });

        await fireEvent.click(getByRole('button'));
        expect(handleClick).toHaveBeenCalled();
    });
});
```

### Context와 함께 테스트

```typescript
import { render } from '@testing-library/svelte';
import { AUTH_CONTEXT_KEY, AuthStore } from '$lib/stores/auth.svelte';
import AuthStatus from './AuthStatus.svelte';

it('Context를 사용하는 컴포넌트', () => {
    const authStore = new AuthStore();
    authStore.token = 'test-token';

    const { getByText } = render(AuthStatus, {
        context: new Map([[AUTH_CONTEXT_KEY, authStore]])
    });

    expect(getByText('로그인됨')).toBeInTheDocument();
});
```

### 테스트 실행

```bash
cd frontend

# 전체 테스트
npm run test

# 감시 모드
npm run test:watch

# 커버리지
npm run test:coverage
```

## 스타일링 (Tailwind CSS)

### 기본 사용

```svelte
<div class="flex items-center justify-between p-4 bg-gray-100 rounded-lg">
    <h1 class="text-2xl font-bold text-gray-900">제목</h1>
    <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
        버튼
    </button>
</div>
```

### 반응형 디자인

```svelte
<!-- sm: 640px, md: 768px, lg: 1024px, xl: 1280px -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="p-4 bg-white shadow">카드 1</div>
    <div class="p-4 bg-white shadow">카드 2</div>
    <div class="p-4 bg-white shadow">카드 3</div>
</div>
```

## 다음 단계

- [API 레퍼런스](./api-reference.md) - API 명세
- [테스트 가이드](./testing.md) - 테스트 상세

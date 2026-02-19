/**
 * 인증 상태 관리 스토어 (Svelte 5 Runes 패턴).
 *
 * 주요 기능:
 * - 토큰을 localStorage에 저장하여 새로고침 후에도 로그인 유지
 * - 앱 시작 시 저장된 토큰 유효성 검증
 * - 토큰 만료 시 자동 갱신 시도
 * - 401 응답 시 토큰 갱신 또는 로그아웃 처리
 */

import type { User } from '$lib/api';
import { getCurrentUser, refreshToken } from '$lib/api';

export class AuthStore {
    token = $state<string | null>(null);
    user = $state<User | null>(null);
    isLoading = $state(false);
    isInitialized = $state(false);

    // 파생 상태: 토큰이 있고 로딩 중이 아니면 인증됨
    isAuthenticated = $derived(!!this.token && !this.isLoading);

    constructor() {
        // SSR 환경에서는 localStorage 접근 불가하므로 브라우저 확인
        if (typeof window !== 'undefined') {
            this.token = localStorage.getItem('access_token');
        }
    }

    /**
     * 앱 시작 시 인증 상태 초기화.
     *
     * +layout.svelte의 onMount에서 호출하여:
     * 1. localStorage에 저장된 토큰이 있는지 확인
     * 2. 토큰으로 /me API 호출하여 유효성 검증
     * 3. 만료되었으면 refresh 시도, 실패하면 로그아웃
     */
    async initialize(): Promise<void> {
        if (this.isInitialized) return;

        if (!this.token) {
            this.isInitialized = true;
            return;
        }

        this.isLoading = true;

        try {
            // 토큰으로 사용자 정보 조회하여 유효성 검증
            const user = await getCurrentUser(this.token);
            this.user = user;
        } catch (error) {
            // 토큰이 만료되었거나 유효하지 않음 → 갱신 시도
            const refreshed = await this.tryRefreshToken();
            if (!refreshed) {
                // 갱신 실패 → 완전히 로그아웃
                this.logout();
            }
        } finally {
            this.isLoading = false;
            this.isInitialized = true;
        }
    }

    /**
     * 토큰 갱신 시도.
     *
     * Access token이 만료되었을 때 refresh token으로 새 토큰 발급.
     * 백엔드에서 기존 토큰을 받아 새 토큰을 반환하는 방식.
     */
    private async tryRefreshToken(): Promise<boolean> {
        if (!this.token) return false;

        try {
            const result = await refreshToken(this.token);
            this.setToken(result.access_token);

            // 새 토큰으로 사용자 정보 다시 조회
            const user = await getCurrentUser(result.access_token);
            this.user = user;

            return true;
        } catch {
            return false;
        }
    }

    /**
     * API 401 응답 처리.
     *
     * API 호출 중 401(Unauthorized)을 받으면 이 메서드 호출.
     * 토큰 갱신을 시도하고, 실패하면 로그아웃하여 로그인 페이지로 유도.
     */
    async handleUnauthorized(): Promise<boolean> {
        const refreshed = await this.tryRefreshToken();
        if (!refreshed) {
            this.logout();
        }
        return refreshed;
    }

    setToken(token: string) {
        this.token = token;
        if (typeof window !== 'undefined') {
            localStorage.setItem('access_token', token);
        }
    }

    setUser(user: User) {
        this.user = user;
    }

    logout() {
        this.token = null;
        this.user = null;
        if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
        }
    }

    getAuthHeaders(): Record<string, string> {
        if (!this.token) return {};
        return { 'Authorization': `Bearer ${this.token}` };
    }
}

// Context key for type-safe context access
export const AUTH_CONTEXT_KEY = Symbol('auth');

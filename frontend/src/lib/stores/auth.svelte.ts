/**
 * Auth Store - Reactive Class Pattern for Svelte 5
 *
 * Manages authentication state reactively.
 * Syncs with localStorage for persistence.
 * Handles token validation and user loading.
 */

import type { User } from '$lib/api';
import { getCurrentUser, refreshToken } from '$lib/api';

export class AuthStore {
    token = $state<string | null>(null);
    user = $state<User | null>(null);
    isLoading = $state(false);
    isInitialized = $state(false);

    // Derived state
    isAuthenticated = $derived(!!this.token && !this.isLoading);

    constructor() {
        // Initialize from localStorage if in browser
        if (typeof window !== 'undefined') {
            this.token = localStorage.getItem('access_token');
        }
    }

    /**
     * Initialize auth state from stored token.
     * Call this from layout's onMount to validate stored token and load user.
     */
    async initialize(): Promise<void> {
        if (this.isInitialized) return;

        if (!this.token) {
            this.isInitialized = true;
            return;
        }

        this.isLoading = true;

        try {
            // Validate token by fetching user info
            const user = await getCurrentUser(this.token);
            this.user = user;
        } catch (error) {
            // Token is invalid or expired, try to refresh
            const refreshed = await this.tryRefreshToken();
            if (!refreshed) {
                // Refresh failed, clear auth state
                this.logout();
            }
        } finally {
            this.isLoading = false;
            this.isInitialized = true;
        }
    }

    /**
     * Attempt to refresh the access token.
     * Returns true if successful, false otherwise.
     */
    private async tryRefreshToken(): Promise<boolean> {
        if (!this.token) return false;

        try {
            const result = await refreshToken(this.token);
            this.setToken(result.access_token);

            // Fetch user with new token
            const user = await getCurrentUser(result.access_token);
            this.user = user;

            return true;
        } catch {
            return false;
        }
    }

    /**
     * Handle 401 errors from API calls.
     * Call this when receiving unauthorized errors.
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

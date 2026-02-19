/**
 * Auth Store - Reactive Class Pattern for Svelte 5
 *
 * Manages authentication state reactively.
 * Syncs with localStorage for persistence.
 */

import type { User } from '$lib/api';

export class AuthStore {
    token = $state<string | null>(null);
    user = $state<User | null>(null);
    isLoading = $state(false);

    // Derived state
    isAuthenticated = $derived(!!this.token);

    constructor() {
        // Initialize from localStorage if in browser
        if (typeof window !== 'undefined') {
            this.token = localStorage.getItem('access_token');
        }
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

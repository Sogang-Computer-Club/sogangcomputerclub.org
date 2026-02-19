/**
 * UI Store - Reactive Class Pattern for Svelte 5
 *
 * Manages global UI state like mobile menu visibility.
 * Use with Context API for testability and component isolation.
 */

export class UIStore {
    isMobileMenuOpen = $state(false);

    toggle() {
        this.isMobileMenuOpen = !this.isMobileMenuOpen;
    }

    open() {
        this.isMobileMenuOpen = true;
    }

    close() {
        this.isMobileMenuOpen = false;
    }
}

// Context key for type-safe context access
export const UI_CONTEXT_KEY = Symbol('ui');

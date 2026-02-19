import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import Header from './Header.svelte';
import { UIStore, UI_CONTEXT_KEY } from '$lib/stores';

describe('Header', () => {
	let uiStore: UIStore;

	beforeEach(() => {
		// Create fresh UIStore for each test
		uiStore = new UIStore();

		// Mock window.innerWidth
		Object.defineProperty(window, 'innerWidth', {
			writable: true,
			configurable: true,
			value: 1024
		});
	});

	const renderWithContext = () => {
		return render(Header, {
			context: new Map([[UI_CONTEXT_KEY, uiStore]])
		});
	};

	it('should render the header with logo and title', () => {
		renderWithContext();

		// Check if SGCC title is rendered
		expect(screen.getByText('SGCC')).toBeInTheDocument();
		expect(screen.getByText('Sogang computer club')).toBeInTheDocument();

		// Check if logo link exists
		const logoLink = screen.getByRole('link', { name: /main menu/i });
		expect(logoLink).toBeInTheDocument();
		expect(logoLink).toHaveAttribute('href', '/');
	});

	it('should have correct navigation structure', () => {
		renderWithContext();

		// Check header element exists
		const header = document.querySelector('header');
		expect(header).toBeInTheDocument();

		// Check nav element exists
		const nav = document.querySelector('nav');
		expect(nav).toBeInTheDocument();
	});

	it('should toggle mobile menu when button is clicked', async () => {
		// Set mobile viewport
		Object.defineProperty(window, 'innerWidth', {
			writable: true,
			configurable: true,
			value: 768
		});

		renderWithContext();

		// Find the open menu button
		const openMenuButton = screen.getByRole('button', { name: /open menu/i });
		expect(openMenuButton).toBeInTheDocument();

		// Click to open menu
		await fireEvent.click(openMenuButton);

		// Check if close button appears (should have multiple, checking for any)
		const closeMenuButtons = screen.getAllByRole('button', { name: /close menu/i });
		expect(closeMenuButtons.length).toBeGreaterThan(0);
	});

	it('should render mobile menu icon on small screens', () => {
		// Set mobile viewport before render
		Object.defineProperty(window, 'innerWidth', {
			writable: true,
			configurable: true,
			value: 768
		});

		// Trigger resize event
		window.dispatchEvent(new Event('resize'));

		renderWithContext();

		// Mobile menu button should be visible - check if it exists in DOM
		// In jsdom, desktop:hidden class should make it visible on mobile
		const buttons = document.querySelectorAll('button[aria-label]');
		const hasMenuButton = Array.from(buttons).some(
			(btn) =>
				btn.getAttribute('aria-label')?.toLowerCase().includes('menu') ||
				btn.getAttribute('aria-label')?.toLowerCase().includes('open')
		);
		expect(hasMenuButton).toBe(true);
	});

	it('should have accessible labels for buttons', () => {
		Object.defineProperty(window, 'innerWidth', {
			writable: true,
			configurable: true,
			value: 768
		});

		window.dispatchEvent(new Event('resize'));

		renderWithContext();

		// Check aria-label attributes exist on buttons
		const buttons = document.querySelectorAll('button[aria-label]');
		const hasAccessibleButton = Array.from(buttons).some((btn) =>
			btn.hasAttribute('aria-label')
		);
		expect(hasAccessibleButton).toBe(true);
	});

	it('should verify UIStore integration', async () => {
		// Start with menu closed
		expect(uiStore.isMobileMenuOpen).toBe(false);

		Object.defineProperty(window, 'innerWidth', {
			writable: true,
			configurable: true,
			value: 768
		});

		renderWithContext();

		// Click to open menu
		const openMenuButton = screen.getByRole('button', { name: /open menu/i });
		await fireEvent.click(openMenuButton);

		// Verify store state changed
		expect(uiStore.isMobileMenuOpen).toBe(true);
	});
});

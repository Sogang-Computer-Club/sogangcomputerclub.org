// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

// Declare private environment variables
declare module '$env/static/private' {
	export const GOOGLE_API_KEY: string;
	export const CALENDAR_ID: string;
}

export {};

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

declare namespace svelteHTML {
	interface HTMLAttributes<T> extends AriaAttributes, DOMAttributes<T> {
		[key: string]: any;
	}
}

interface AriaAttributes {
	[key: string]: any;
}

interface DOMAttributes<T> {
	[key: string]: any;
}

export {};

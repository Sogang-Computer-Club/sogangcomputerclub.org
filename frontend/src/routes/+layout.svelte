<script lang="ts">
    import { setContext } from 'svelte';
    import { UIStore, UI_CONTEXT_KEY, AuthStore, AUTH_CONTEXT_KEY } from '$lib/stores';
    import "../app.css";
    import { page } from '$app/state';

    import Header from "../lib/components/Header.svelte"
    import Footer from "../lib/components/Footer.svelte"

    let { children } = $props();

    // Provide stores via Context API
    const uiStore = new UIStore();
    const authStore = new AuthStore();

    setContext(UI_CONTEXT_KEY, uiStore);
    setContext(AUTH_CONTEXT_KEY, authStore);
</script>


<div class="font-[Pretendard_Variable]">
<Header />
{@render children()}
{#if page.url.pathname !== '/login' && page.url.pathname !== '/' && page.url.pathname !== '/sign-up'}
  <footer><Footer /></footer>
{/if}
</div>
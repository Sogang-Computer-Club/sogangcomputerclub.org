<script lang="ts">
    import { setContext } from 'svelte';
    import { UIStore, UI_CONTEXT_KEY } from '$lib/stores';
    import "../app.css";
    import { page } from '$app/state';

    import Header from "../lib/components/Header.svelte"
    import Footer from "../lib/components/Footer.svelte"

    let { children } = $props();

    // Provide stores via Context API
    const uiStore = new UIStore();
    setContext(UI_CONTEXT_KEY, uiStore);
</script>


<div class="font-[Pretendard_Variable]">
<Header />
{@render children()}
{#if page.url.pathname !== '/'}
  <footer><Footer /></footer>
{/if}
</div>
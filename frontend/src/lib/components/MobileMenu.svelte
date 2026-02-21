<script lang="ts">
    import { getContext } from 'svelte';
    import { UI_CONTEXT_KEY, type UIStore } from '$lib/stores';
    import { navItems } from '$lib/config/navigation';

    const ui = getContext<UIStore>(UI_CONTEXT_KEY);

    let openSubMenu = $state<string | null>(null);

    function toggleSubMenu(menuName: string): void {
        openSubMenu = openSubMenu === menuName ? null : menuName;
    }

    function handleNavigate(): void {
        ui.close();
        openSubMenu = null;
    }
</script>

<div class="relative flex bg-black w-full h-full py-1.5">
    <div
        class="flex flex-col desktop:hidden w-41 h-full font-normal text-[20px] pl-8 pr-0.75 border-r-white border-r-[1px]"
        role="navigation"
    >
        {#each navItems as item}
            <div class="relative">
                <!-- Menu Elements -->
                <button
                    onclick={(e) => { e.preventDefault(); toggleSubMenu(item.name); }}
                    class="flex relative w-full h-19.5 items-center text-white font-sogang hover:text-gray-200 transition-colors duration-300
                    after:content-[''] after:absolute after:right-0 after:translate-x-1/2 after:h-0 after:w-1.25 after:bg-[#AE1F1F] after:transition-all after:duration-200
                    hover:cursor-pointer {openSubMenu === item.name
                        ? 'after:h-full'
                        : '!after:h-full'}"
                >
                    {item.name}
                </button>

                {#if openSubMenu === item.name && item.subItems.length > 0}
                    <!-- Notice 배치 조절.... -->
                    {#if openSubMenu == "Notice"}
                        <div
                            class="absolute z-10 left-full -top-21 h-[250px] w-screen transform shadow-lg transition-all duration-300 visible opacity-90"
                        >
                            <div
                                class="absolute flex w-[50%] max-w-[786px] text-left text-[18px] text-white font-pretendard-variable [&>div]:pl-9.5"
                            >
                                <div class="flex-1 min-w-[60px] h-[250px]">
                                    <ul class="mt-1.5 [&>li]:h-19.5">
                                        {#each item.subItems as subItem}
                                            <li>
                                                <a
                                                    href={subItem.path}
                                                    onclick={handleNavigate}
                                                    class="flex h-full items-center transition-colors hover:text-red-600"
                                                    >{subItem.name}</a
                                                >
                                            </li>
                                        {/each}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    {:else}
                        <!-- 나머지 메뉴 -->
                        <div
                            class="absolute z-10 left-full -top-1.5 h-[250px] w-screen transform shadow-lg transition-all duration-300 visible opacity-90"
                        >
                            <div
                                class="absolute flex w-[50%] max-w-[786px] text-left text-[18px] text-white font-pretendard-variable [&>div]:pl-9.5"
                            >
                                <div class="flex-1 min-w-[60px] h-[250px]">
                                    <ul class="mt-1.5 [&>li]:h-19.5">
                                        {#each item.subItems as subItem}
                                            <li>
                                                <a
                                                    href={subItem.path}
                                                    onclick={handleNavigate}
                                                    class="flex h-full items-center transition-colors hover:text-red-600"
                                                    >{subItem.name}</a
                                                >
                                            </li>
                                        {/each}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    {/if}
                {/if}
            </div>
        {/each}
        <div class="flex flex-col text-white mt-auto -translate-y-18">
            <a
                href="/login"
                onclick={handleNavigate}
                class="min-w-[60px] h-12 mt-auto text-[20px]"
            >
                Login
            </a>
            <a
                href="/sign-up"
                onclick={handleNavigate}
                class="min-w-[60px] h-12 mt-auto text-[20px]"
            >
                Sign Up
            </a>
        </div>
    </div>
</div>

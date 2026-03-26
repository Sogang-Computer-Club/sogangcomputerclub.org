<script lang="ts">
    import { navItems } from "$lib/config/navigation";
</script>

<div class="hidden desktop:flex w-full h-full items-center">
    <div
        class="group absolute left-1/2 h-full w-[50%] max-w-[786px] -translate-x-1/2"
    >
        <div
            class="flex h-full text-[16px] font-sogang font-normal"
            role="navigation"
        >
            {#each navItems as item}
                <div
                    class="relative flex flex-1 min-w-[60px] items-center justify-center text-white transition-colors duration-300 after:absolute after:bottom-0 after:left-1/2 after:h-1 after:w-0 after:-translate-x-1/2 after:bg-[#AE1F1F] after:transition-all after:duration-200 after:content-[''] hover:text-gray-200 hover:neon-text hover:after:w-full select-none cursor-default"
                >
                    {item.name}
                </div>
            {/each}
        </div>

        <div
            class="absolute left-1/2 top-full z-10 h-[250px] w-screen -translate-x-1/2 translate-y-[-10px] transform invisible opacity-0 shadow-lg transition-all duration-300 group-hover:visible group-hover:translate-y-0 group-hover:opacity-100 bg-[#8D1F1F]"
        >
            <div
                class="absolute left-1/2 flex w-[50%] max-w-[786px] -translate-x-1/2 text-left text-[18px] text-white [&>div]:pl-5"
            >
                {#each navItems as item, i}
                    <div
                        class="flex-1 min-w-[60px] h-[250px] border-r-1 border-r-white{i === 0
                            ? ' border-l-1 border-l-white'
                            : ''}"
                    >
                        <ul class="[&>li]:mt-4.25">
                            {#each item.subItems as subItem}
                                <li>
                                    <a
                                        href={subItem.path}
                                        class="block transition-colors hover:text-gray-300 font-pretendard-variable"
                                        >{subItem.name}</a
                                    >
                                </li>
                            {/each}
                        </ul>
                    </div>
                {/each}
            </div>
        </div>
    </div>

</div>

<script lang="ts">
    import 'highlight.js/styles/github-dark.css';
    import '$lib/styles/markdown-content.css';
    import { renderMarkdown, debounce } from '$lib/utils/markdown';
    import type { Memo } from '$lib/api';
    import { createMemo } from '$lib/api';

    interface Props {
        onMemoCreate?: (memo: Memo) => void;
    }

    let { onMemoCreate }: Props = $props();

    let memoTitle = $state('');
    let memoText = $state('');
    let markdownRenderedMemoText = $state('');
    let isModalOpen = $state(false);

    const debouncedUpdate = debounce((text: string) => {
        markdownRenderedMemoText = renderMarkdown(text);
    }, 300);

    $effect(() => {
        debouncedUpdate(memoText);
    });

    function openModal() {
        isModalOpen = true;
    }

    function closeModal() {
        memoTitle = '';
        memoText = '';
        isModalOpen = false;
    }

    async function saveMemo() {
        if (!memoTitle.trim() || !memoText.trim()) {
            alert('제목과 내용을 모두 입력해주세요.');
            return;
        }

        try {
            const newMemo = await createMemo({
                title: memoTitle.trim(),
                content: memoText.trim()
            });
            closeModal();
            onMemoCreate?.(newMemo);
        } catch (error) {
            console.error('Failed to create memo:', error);
            alert(`메모 생성에 실패했습니다. ${error}`);
        }
    }
</script>

<div
    class="break-inside-avoid w-60 h-60 p-4 bg-[#FFF3DF] border-[#200F4C] border-2 border-dashed cursor-pointer rounded-lg m-4 text-6xl hover:text-7xl transition duration-150 ease-out flex items-center justify-center"
    onclick={openModal}
    onkeydown={(e) => e.key === 'Enter' && openModal()}
    role="button"
    tabindex="0"
>
    <span class="text-[#200F4C] transition duration-150 ease-out">+</span>
</div>

{#if isModalOpen}
    <div class="fixed inset-0 bg-black/70 z-40 flex flex-col items-center justify-center">
        <div
            class="w-[80vw] h-[80vh] bg-[#200F4C] rounded-lg z-50 p-4 flex flex-col gap-4"
        >
            <input
                class="text-4xl text-[#FFF3DF] font-black font-[Pretendard_Variable] border-b-1 border-[#FFF3DF] pb-2 focus:outline-none bg-transparent"
                bind:value={memoTitle}
                placeholder="메모 제목을 입력하세요..."
            />
            <div class="flex-1 grid grid-cols-2 gap-4 min-h-0">
                <textarea
                    class="resize-none focus:outline-none h-full min-h-0 overflow-y-auto text-[#FFF3DF] font-[Ubuntu_Mono] bg-transparent"
                    bind:value={memoText}
                    placeholder="메모 내용을 입력하세요..."
                ></textarea>
                <div
                    class="markdown-content h-full min-h-0 overflow-y-auto overflow-x-hidden break-words text-[#FFF3DF]"
                >
                    {@html markdownRenderedMemoText}
                </div>
            </div>
        </div>

        <div class="flex justify-end w-[80vw] mt-4">
            <button
                class="bg-[#FFF3DF] text-[#200F4C] m-2 px-8 py-4 text-lg font-bold rounded-2xl cursor-pointer transition duration-150 ease-out"
                onclick={closeModal}
            >
                취소
            </button>
            <button
                class="bg-[#200F4C] text-[#FFF3DF] m-2 px-8 py-4 text-lg font-bold rounded-2xl cursor-pointer transition duration-150 ease-out"
                onclick={saveMemo}
            >
                생성
            </button>
        </div>
    </div>
{/if}

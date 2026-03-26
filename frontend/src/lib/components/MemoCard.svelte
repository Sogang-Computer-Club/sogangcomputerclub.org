<script lang="ts">
    import 'highlight.js/styles/github-dark.css';
    import '$lib/styles/markdown-content.css';
    import { renderMarkdown, debounce } from '$lib/utils/markdown';
    import type { Memo } from '$lib/api';
    import { updateMemo, deleteMemo } from '$lib/api';

    interface Props {
        memo: Memo;
        memoColor: string;
        onMemoUpdate?: (updatedMemo: Memo) => void;
        onMemoDelete?: (deletedId: number) => void;
    }

    let { memo, memoColor, onMemoUpdate, onMemoDelete }: Props = $props();

    // Local editing state (copy on edit pattern)
    let memoText = $state(memo.content);
    let memoTitle = $state(memo.title);
    let markdownRenderedMemoText = $state('');
    let isModalOpen = $state(false);

    // Sync local state when prop changes
    $effect(() => {
        memoText = memo.content;
        memoTitle = memo.title;
    });

    const debouncedUpdate = debounce((text: string) => {
        markdownRenderedMemoText = renderMarkdown(text);
    }, 300);

    $effect(() => {
        debouncedUpdate(memoText);
    });

    function openModal() {
        memoText = memo.content;
        memoTitle = memo.title;
        isModalOpen = true;
    }

    function closeModal() {
        isModalOpen = false;
    }

    async function saveMemo() {
        try {
            const updatedMemo = await updateMemo(memo.id, {
                title: memoTitle,
                content: memoText
            });
            closeModal();
            // Notify parent via callback instead of location.reload()
            onMemoUpdate?.(updatedMemo);
        } catch (error) {
            console.error('Failed to update memo:', error);
            alert('메모 저장에 실패했습니다.');
        }
    }

    async function handleDeleteMemo() {
        if (confirm('정말로 이 메모를 삭제하시겠습니까?')) {
            try {
                await deleteMemo(memo.id);
                closeModal();
                // Notify parent via callback instead of location.reload()
                onMemoDelete?.(memo.id);
            } catch (error) {
                console.error('Failed to delete memo:', error);
                alert('메모 삭제에 실패했습니다.');
            }
        }
    }
</script>

<div
    class="break-inside-avoid w-60 min-h-60 p-4 border-2 cursor-pointer rounded-lg m-4 transition duration-150 ease-out break-words"
    style="background-color: {memoColor}; border-color: {memoColor}"
    onclick={openModal}
    onkeydown={(e) => e.key === 'Enter' && openModal()}
    role="button"
    tabindex="0"
>
    <div class="font-black text-[#FFF3DF] font-[Pretendard_Variable] text-2xl mb-2 truncate">
        {memo.title}
    </div>
    <div class="text-xs text-[#FFF3DF] font-[Ubuntu_Mono]">
        {memo.content.length <= 500 ? memo.content : memo.content.substring(0, 500) + '...'}
    </div>
</div>

{#if isModalOpen}
    <div class="fixed inset-0 bg-black/70 z-40 flex flex-col items-center justify-center">
        <div
            class="w-[80vw] h-[80vh] rounded-lg z-50 p-4 flex flex-col gap-4"
            style="background: {memoColor}"
        >
            <input
                class="text-4xl font-black border-b-1 text-[#FFF3DF] font-[Pretendard_Variable] border-[#FFF3DF] pb-2 focus:outline-none focus:border-gray-400 bg-transparent"
                bind:value={memoTitle}
                placeholder="메모 제목"
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
                onclick={handleDeleteMemo}
            >
                삭제
            </button>
            <button
                class="bg-[#FFF3DF] text-[#200F4C] m-2 px-8 py-4 text-lg font-bold rounded-2xl cursor-pointer transition duration-150 ease-out"
                onclick={closeModal}
            >
                닫기
            </button>
            <button
                class="text-[#FFF3DF] m-2 px-8 py-4 text-lg font-bold rounded-2xl cursor-pointer transition duration-150 ease-out"
                style="background-color: {memoColor};"
                onclick={saveMemo}
            >
                저장
            </button>
        </div>
    </div>
{/if}

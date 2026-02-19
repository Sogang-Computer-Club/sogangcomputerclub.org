<script lang="ts">
    import { getContext } from 'svelte';
    import 'highlight.js/styles/github-dark.css';
    import { marked } from 'marked';
    import DOMPurify from 'dompurify';
    import hljs from 'highlight.js';
    import type { Memo } from '$lib/api';
    import { updateMemo, deleteMemo } from '$lib/api';
    import { AUTH_CONTEXT_KEY, type AuthStore } from '$lib/stores';

    interface Props {
        memo: Memo;
        memoColor: string;
        onMemoUpdate?: (updatedMemo: Memo) => void;
        onMemoDelete?: (deletedId: number) => void;
    }

    let { memo, memoColor, onMemoUpdate, onMemoDelete }: Props = $props();

    const auth = getContext<AuthStore>(AUTH_CONTEXT_KEY);

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

    // Configure marked
    (marked.setOptions as any)({
        highlight: function (code: string, lang: string) {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return hljs.highlight(code, { language: lang }).value;
                } catch (err) {
                    console.error('Highlight error:', err);
                }
            }
            return hljs.highlightAuto(code).value;
        },
        breaks: true,
        gfm: true
    });

    // Debounce function
    function debounce(func: Function, wait: number) {
        let timeout: ReturnType<typeof setTimeout>;
        return function executedFunction(...args: any[]) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    const debouncedUpdate = debounce(async (text: string) => {
        if (text.trim()) {
            const rawHtml = marked.parse(text) as string;
            markdownRenderedMemoText = DOMPurify.sanitize(rawHtml);
        } else {
            markdownRenderedMemoText = '';
        }
    }, 300);

    $effect(() => {
        if (memoText !== undefined) {
            debouncedUpdate(memoText);
        }
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
            }, auth?.token ?? undefined);
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
                await deleteMemo(memo.id, auth?.token ?? undefined);
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

<style>
    :global(.prose pre) {
        background-color: transparent;
    }

    .markdown-content :global(h1),
    .markdown-content :global(h2),
    .markdown-content :global(h3),
    .markdown-content :global(h4),
    .markdown-content :global(h5),
    .markdown-content :global(h6) {
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        font-weight: 600;
    }

    .markdown-content :global(h1) {
        font-size: 2rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
        padding-bottom: 0.5rem;
    }

    .markdown-content :global(h2) {
        font-size: 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.5rem;
    }

    .markdown-content :global(h3) {
        font-size: 1.25rem;
    }

    .markdown-content :global(p) {
        margin-bottom: 1rem;
    }

    .markdown-content :global(a) {
        color: #60a5fa;
        text-decoration: none;
    }

    .markdown-content :global(a:hover) {
        text-decoration: underline;
    }

    .markdown-content :global(code) {
        background: rgba(0, 0, 0, 0.4);
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 0.875em;
    }

    .markdown-content :global(pre) {
        background: rgba(0, 0, 0, 0.4);
        padding: 1rem;
        border-radius: 6px;
        overflow-x: auto;
        margin: 1rem 0;
    }

    .markdown-content :global(pre code) {
        background: none;
        padding: 0;
    }

    .markdown-content :global(blockquote) {
        border-left: 4px solid rgba(255, 255, 255, 0.3);
        padding-left: 1rem;
        margin-left: 0;
        color: rgba(255, 255, 255, 0.7);
        font-style: italic;
    }

    .markdown-content :global(ul),
    .markdown-content :global(ol) {
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }

    .markdown-content :global(li) {
        margin-bottom: 0.25rem;
    }

    .markdown-content :global(table) {
        border-collapse: collapse;
        width: 100%;
        margin: 1rem 0;
    }

    .markdown-content :global(table th),
    .markdown-content :global(table td) {
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 0.5rem;
        text-align: left;
    }

    .markdown-content :global(table th) {
        background: rgba(0, 0, 0, 0.3);
        font-weight: 600;
    }

    .markdown-content :global(img) {
        max-width: 100%;
        height: auto;
        border-radius: 6px;
    }

    .markdown-content :global(hr) {
        border: none;
        border-top: 2px solid rgba(255, 255, 255, 0.2);
        margin: 2rem 0;
    }
</style>

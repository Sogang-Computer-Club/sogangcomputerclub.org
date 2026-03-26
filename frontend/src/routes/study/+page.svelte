<script lang="ts">
    import type { PageData } from './$types';
    import MemoCard from '$lib/components/MemoCard.svelte';
    import MemoPlus from '$lib/components/MemoPlus.svelte';
    import type { Memo } from '$lib/api';

    let { data }: { data: PageData } = $props();

    let memos = $state([...data.memos]);
    let selectedSort = $state('updated');

    const sortedMemos: Memo[] = $derived.by(() => {
        const originalMemos = [...memos];

        switch (selectedSort) {
            case 'newest':
                return originalMemos.sort((a, b) =>
                    new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
                );

            case 'name':
                return originalMemos.sort((a, b) => a.title.localeCompare(b.title));

            case 'updated':
                return originalMemos.sort((a, b) =>
                    new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
                );

            default:
                return originalMemos.sort((a, b) =>
                    new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
                );
        }
    });

    function handleMemoCreate(newMemo: Memo) {
        memos = [...memos, newMemo];
    }

    function handleMemoUpdate(updatedMemo: Memo) {
        memos = memos.map((m) => (m.id === updatedMemo.id ? updatedMemo : m));
    }

    function handleMemoDelete(deletedId: number) {
        memos = memos.filter((m) => m.id !== deletedId);
    }
</script>

<div class="p-4 bg-[#FFF3DF]">
    <label for="sort-select" class="mr-2 font-bold text-[#200F4C]">정렬 기준:</label>
    <select
        bind:value={selectedSort}
        id="sort-select"
        class="p-2 rounded-md bg-[#200F4C] text-[#FFF3DF] focus:outline-none min-w-48"
        style="-webkit-appearance: none; -moz-appearance: none; appearance: none; background-image: url('data:image/svg+xml;charset=US-ASCII,<svg xmlns=&quot;http://www.w3.org/2000/svg&quot; viewBox=&quot;0 0 4 5&quot;><path fill=&quot;%23FFF3DF&quot; d=&quot;M2 0L0 2h4zm0 5L0 3h4z&quot;/></svg>'); background-repeat: no-repeat; background-position: right 0.7em top 50%; background-size: 0.65em auto;"
    >
        <option value="updated">업데이트순 (최신)</option>
        <option value="newest">만든순 (오래된 순)</option>
        <option value="name">이름순</option>
    </select>
</div>

<div class="columns-1 sm:columns-2 md:columns-3 lg:columns-4 xl:columns-5 2xl:columns-6 bg-[#FFF3DF] min-h-screen">
    {#each sortedMemos as memo (memo.id)}
        {#if memo.id % 2 == 0}
            <MemoCard {memo} memoColor="#200F4C" onMemoUpdate={handleMemoUpdate} onMemoDelete={handleMemoDelete} />
        {:else}
            <MemoCard {memo} memoColor="#22949F" onMemoUpdate={handleMemoUpdate} onMemoDelete={handleMemoDelete} />
        {/if}
    {/each}
    <MemoPlus onMemoCreate={handleMemoCreate} />
</div>

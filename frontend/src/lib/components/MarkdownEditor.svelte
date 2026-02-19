<script lang="ts">
    import { onMount } from 'svelte';
    import { marked } from 'marked';
    import DOMPurify from 'dompurify';
    import hljs from 'highlight.js';

    interface Props {
        content?: string;
        onUpdate?: (content: string) => void;
    }

    let { content: initialContent = '', onUpdate }: Props = $props();

    let textarea: HTMLTextAreaElement;
    let content = $state(initialContent);
    let renderedHtml = $state('');

    // Configure marked with syntax highlighting
    onMount(() => {
        (marked.setOptions as any)({
            highlight: function(code: string, lang: string) {
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

        updatePreview();
    });

    function updatePreview() {
        try {
            const rawHtml = marked.parse(content) as string;
            renderedHtml = DOMPurify.sanitize(rawHtml);
        } catch (error) {
            console.error('Markdown parsing error:', error);
            renderedHtml = '<p class="error">Error rendering markdown</p>';
        }
    }

    function handleInput(event: Event) {
        const target = event.target as HTMLTextAreaElement;
        content = target.value;
        onUpdate?.(content);
        updatePreview();
    }

    function handleTab(event: KeyboardEvent) {
        if (event.key === 'Tab') {
            event.preventDefault();
            const target = event.target as HTMLTextAreaElement;
            const start = target.selectionStart;
            const end = target.selectionEnd;

            // Insert tab character
            content = content.substring(0, start) + '  ' + content.substring(end);

            // Move cursor after tab
            setTimeout(() => {
                target.selectionStart = target.selectionEnd = start + 2;
            }, 0);

            onUpdate?.(content);
            updatePreview();
        }
    }
</script>

<div class="markdown-editor">
    <div class="editor-pane">
        <div class="pane-header">
            <h3>Edit</h3>
            <span class="hint">Markdown supported</span>
        </div>
        <textarea
            bind:this={textarea}
            value={content}
            oninput={handleInput}
            onkeydown={handleTab}
            class="editor-textarea"
            placeholder="Write your memo content here... (Markdown supported)"
        ></textarea>
    </div>

    <div class="preview-pane">
        <div class="pane-header">
            <h3>Preview</h3>
        </div>
        <div class="preview-content markdown-body">
            {@html renderedHtml}
        </div>
    </div>
</div>

<style>
    .markdown-editor {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        overflow: hidden;
    }

    .editor-pane,
    .preview-pane {
        display: flex;
        flex-direction: column;
        min-height: 400px;
    }

    .pane-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
        background: rgba(0, 0, 0, 0.3);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .pane-header h3 {
        margin: 0;
        font-size: 0.875rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.9);
    }

    .hint {
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.5);
    }

    .editor-textarea {
        flex: 1;
        padding: 1rem;
        border: none;
        background: rgba(0, 0, 0, 0.2);
        color: white;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 0.875rem;
        line-height: 1.6;
        resize: none;
    }

    .editor-textarea:focus {
        outline: none;
    }

    .preview-pane {
        background: rgba(0, 0, 0, 0.1);
    }

    .preview-content {
        flex: 1;
        padding: 1rem;
        overflow-y: auto;
    }

    /* Markdown Body Styles */
    .markdown-body {
        color: rgba(255, 255, 255, 0.9);
        line-height: 1.6;
    }

    .markdown-body :global(h1),
    .markdown-body :global(h2),
    .markdown-body :global(h3),
    .markdown-body :global(h4),
    .markdown-body :global(h5),
    .markdown-body :global(h6) {
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        font-weight: 600;
        color: white;
    }

    .markdown-body :global(h1) {
        font-size: 2rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
        padding-bottom: 0.5rem;
    }

    .markdown-body :global(h2) {
        font-size: 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.5rem;
    }

    .markdown-body :global(h3) {
        font-size: 1.25rem;
    }

    .markdown-body :global(p) {
        margin-bottom: 1rem;
    }

    .markdown-body :global(a) {
        color: #60a5fa;
        text-decoration: none;
    }

    .markdown-body :global(a:hover) {
        text-decoration: underline;
    }

    .markdown-body :global(code) {
        background: rgba(0, 0, 0, 0.4);
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 0.875em;
    }

    .markdown-body :global(pre) {
        background: rgba(0, 0, 0, 0.4);
        padding: 1rem;
        border-radius: 6px;
        overflow-x: auto;
        margin: 1rem 0;
    }

    .markdown-body :global(pre code) {
        background: none;
        padding: 0;
    }

    .markdown-body :global(blockquote) {
        border-left: 4px solid rgba(255, 255, 255, 0.3);
        padding-left: 1rem;
        margin-left: 0;
        color: rgba(255, 255, 255, 0.7);
        font-style: italic;
    }

    .markdown-body :global(ul),
    .markdown-body :global(ol) {
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }

    .markdown-body :global(li) {
        margin-bottom: 0.25rem;
    }

    .markdown-body :global(table) {
        border-collapse: collapse;
        width: 100%;
        margin: 1rem 0;
    }

    .markdown-body :global(table th),
    .markdown-body :global(table td) {
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 0.5rem;
        text-align: left;
    }

    .markdown-body :global(table th) {
        background: rgba(0, 0, 0, 0.3);
        font-weight: 600;
    }

    .markdown-body :global(img) {
        max-width: 100%;
        height: auto;
        border-radius: 6px;
    }

    .markdown-body :global(hr) {
        border: none;
        border-top: 2px solid rgba(255, 255, 255, 0.2);
        margin: 2rem 0;
    }

    .markdown-body :global(.error) {
        color: #ef4444;
        padding: 1rem;
        background: rgba(239, 68, 68, 0.1);
        border-radius: 6px;
    }

    @media (max-width: 768px) {
        .markdown-editor {
            grid-template-columns: 1fr;
        }

        .preview-pane {
            min-height: 300px;
        }
    }
</style>

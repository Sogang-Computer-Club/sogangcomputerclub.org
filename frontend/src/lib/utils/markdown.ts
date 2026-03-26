import { marked } from "marked";
import DOMPurify from "dompurify";
import hljs from "highlight.js/lib/core";

// Register only the languages actually used in the project
// Add more as needed: import lang from "highlight.js/lib/languages/{name}"
import javascript from "highlight.js/lib/languages/javascript";
import typescript from "highlight.js/lib/languages/typescript";
import python from "highlight.js/lib/languages/python";
import bash from "highlight.js/lib/languages/bash";
import json from "highlight.js/lib/languages/json";
import css from "highlight.js/lib/languages/css";
import xml from "highlight.js/lib/languages/xml";

hljs.registerLanguage("javascript", javascript);
hljs.registerLanguage("typescript", typescript);
hljs.registerLanguage("python", python);
hljs.registerLanguage("bash", bash);
hljs.registerLanguage("json", json);
hljs.registerLanguage("css", css);
hljs.registerLanguage("xml", xml);
hljs.registerLanguage("html", xml);

/**
 * Configure marked with syntax highlighting and GFM.
 * Call once at module level.
 */
function configureMarked(): void {
  (marked.setOptions as any)({
    highlight: function (code: string, lang: string) {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return hljs.highlight(code, { language: lang }).value;
        } catch (err) {
          console.error("Highlight error:", err);
        }
      }
      // Fall back to auto-detect among registered languages
      return hljs.highlightAuto(code).value;
    },
    breaks: true,
    gfm: true,
  });
}

/**
 * Render markdown to sanitized HTML.
 */
export function renderMarkdown(text: string): string {
  if (!text.trim()) return "";
  const rawHtml = marked.parse(text) as string;
  return DOMPurify.sanitize(rawHtml);
}

/**
 * Debounce a function call.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function debounce<T extends (...args: any[]) => void>(
  func: T,
  wait: number,
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout>;
  return function (...args: Parameters<T>) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Auto-configure on import
configureMarked();

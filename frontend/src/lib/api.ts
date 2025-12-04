// API configuration
// Use full URL for SSR, relative URL for client
const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL || (typeof window === 'undefined'
    ? 'http://sgcc-backend:8000'
    : '/api');

export interface Memo {
    id: number;
    title: string;
    content: string;
    tags: string[];
    priority: number;
    category: string | null;
    is_archived: boolean;
    is_favorite: boolean;
    author: string | null;
    created_at: string;
    updated_at: string;
}

export interface MemoCreate {
    title: string;
    content: string;
    tags?: string[];
    priority?: number;
    category?: string | null;
    is_archived?: boolean;
    is_favorite?: boolean;
    author?: string | null;
}

export interface MemoUpdate {
    title?: string;
    content?: string;
    tags?: string[];
    priority?: number;
    category?: string | null;
    is_archived?: boolean;
    is_favorite?: boolean;
    author?: string | null;
}

/**
 * Fetch all memos
 */
export async function getMemos(skip: number = 0, limit: number = 100): Promise<Memo[]> {
    const response = await fetch(`${API_BASE_URL}/memos/?skip=${skip}&limit=${limit}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch memos: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Fetch a single memo by ID
 */
export async function getMemo(id: number): Promise<Memo> {
    const response = await fetch(`${API_BASE_URL}/memos/${id}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch memo ${id}: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Create a new memo
 */
export async function createMemo(memo: MemoCreate): Promise<Memo> {
    const response = await fetch(`${API_BASE_URL}/memos/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(memo),
    });
    if (!response.ok) {
        throw new Error(`Failed to create memo: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Update an existing memo
 */
export async function updateMemo(id: number, memo: MemoUpdate): Promise<Memo> {
    const response = await fetch(`${API_BASE_URL}/memos/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(memo),
    });
    if (!response.ok) {
        throw new Error(`Failed to update memo ${id}: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Delete a memo
 */
export async function deleteMemo(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/memos/${id}`, {
        method: 'DELETE',
    });
    if (!response.ok) {
        throw new Error(`Failed to delete memo ${id}: ${response.statusText}`);
    }
}

/**
 * Search memos
 */
export async function searchMemos(query: string): Promise<Memo[]> {
    const response = await fetch(`${API_BASE_URL}/memos/search/?q=${encodeURIComponent(query)}`);
    if (!response.ok) {
        throw new Error(`Failed to search memos: ${response.statusText}`);
    }
    return response.json();
}

/**
 * API 클라이언트 설정.
 *
 * SSR vs CSR 환경에 따라 다른 URL 사용:
 * - SSR (서버): Docker 내부 네트워크로 직접 백엔드 호출 (http://backend:8000)
 * - CSR (브라우저): Vite 프록시를 통해 호출 (/api → localhost:8000)
 */
const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL || (typeof window === 'undefined'
    ? 'http://backend:8000/v1'
    : '/api/v1');

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

export interface ApiError {
    detail: string;
    status: number;
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    email: string;
    password: string;
    name: string;
    student_id?: string;
}

export interface AuthToken {
    access_token: string;
    token_type: string;
}

export interface User {
    id: number;
    email: string;
    name: string;
    student_id: string | null;
    is_active: boolean;
    is_admin: boolean;
    created_at: string;
    updated_at: string;
}

/**
 * Helper to extract error message from response
 */
async function handleApiError(response: Response, defaultMessage: string): Promise<never> {
    let detail = defaultMessage;
    try {
        const errorBody = await response.json();
        if (errorBody.detail) {
            detail = errorBody.detail;
        }
    } catch {
        // Use default message if body can't be parsed
    }

    const error = new Error(detail) as Error & { status: number };
    error.status = response.status;
    throw error;
}

/**
 * Get authorization headers if token is available
 */
function getAuthHeaders(token?: string): HeadersInit {
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

/**
 * Fetch all memos
 */
export async function getMemos(skip: number = 0, limit: number = 100): Promise<Memo[]> {
    const response = await fetch(`${API_BASE_URL}/memos/?skip=${skip}&limit=${limit}`);
    if (!response.ok) {
        await handleApiError(response, `Failed to fetch memos: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Fetch a single memo by ID
 */
export async function getMemo(id: number): Promise<Memo> {
    const response = await fetch(`${API_BASE_URL}/memos/${id}`);
    if (!response.ok) {
        await handleApiError(response, `Failed to fetch memo ${id}: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Create a new memo (requires authentication)
 * @param memo - The memo data to create
 * @param token - Optional auth token. If not provided, request will fail with 401.
 */
export async function createMemo(memo: MemoCreate, token?: string): Promise<Memo> {
    const response = await fetch(`${API_BASE_URL}/memos/`, {
        method: 'POST',
        headers: getAuthHeaders(token),
        body: JSON.stringify(memo),
    });
    if (!response.ok) {
        await handleApiError(response, `Failed to create memo: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Update an existing memo (requires authentication)
 * @param id - The memo ID to update
 * @param memo - The updated memo data
 * @param token - Optional auth token. If not provided, request will fail with 401.
 */
export async function updateMemo(id: number, memo: MemoUpdate, token?: string): Promise<Memo> {
    const response = await fetch(`${API_BASE_URL}/memos/${id}`, {
        method: 'PUT',
        headers: getAuthHeaders(token),
        body: JSON.stringify(memo),
    });
    if (!response.ok) {
        await handleApiError(response, `Failed to update memo ${id}: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Delete a memo (requires authentication)
 * @param id - The memo ID to delete
 * @param token - Optional auth token. If not provided, request will fail with 401.
 */
export async function deleteMemo(id: number, token?: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/memos/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders(token),
    });
    if (!response.ok) {
        await handleApiError(response, `Failed to delete memo ${id}: ${response.statusText}`);
    }
}

/**
 * Search memos with pagination
 */
export async function searchMemos(
    query: string,
    skip: number = 0,
    limit: number = 100
): Promise<Memo[]> {
    const params = new URLSearchParams({
        q: query,
        skip: skip.toString(),
        limit: limit.toString(),
    });
    const response = await fetch(`${API_BASE_URL}/memos/search/?${params}`);
    if (!response.ok) {
        await handleApiError(response, `Failed to search memos: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Login user and return access token
 */
export async function login(credentials: LoginRequest): Promise<AuthToken> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
    });
    if (!response.ok) {
        await handleApiError(response, 'Login failed');
    }
    return response.json();
}

/**
 * Register a new user
 */
export async function register(userData: RegisterRequest): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
    });
    if (!response.ok) {
        await handleApiError(response, 'Registration failed');
    }
    return response.json();
}

/**
 * Get current user info
 */
export async function getCurrentUser(token: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: getAuthHeaders(token),
    });
    if (!response.ok) {
        await handleApiError(response, 'Failed to get user info');
    }
    return response.json();
}

/**
 * Refresh access token
 */
export async function refreshToken(token: string): Promise<AuthToken> {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: getAuthHeaders(token),
    });
    if (!response.ok) {
        await handleApiError(response, 'Token refresh failed');
    }
    return response.json();
}

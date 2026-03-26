/**
 * API 클라이언트 설정.
 *
 * SSR vs CSR 환경에 따라 다른 URL 사용:
 * - SSR (서버): Docker 내부 네트워크로 직접 백엔드 호출 (http://backend:8000)
 * - CSR (브라우저): Vite 프록시를 통해 호출 (/api → localhost:8000)
 */
const API_BASE_URL =
  import.meta.env.PUBLIC_API_BASE_URL ||
  (typeof window === "undefined" ? "http://backend:8000/v1" : "/api/v1");

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
 * Helper to extract error message from response
 */
async function handleApiError(
  response: Response,
  defaultMessage: string,
): Promise<never> {
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
 * Fetch all memos
 */
export async function getMemos(
  skip: number = 0,
  limit: number = 100,
): Promise<Memo[]> {
  const response = await fetch(
    `${API_BASE_URL}/memos/?skip=${skip}&limit=${limit}`,
  );
  if (!response.ok) {
    await handleApiError(
      response,
      `Failed to fetch memos: ${response.statusText}`,
    );
  }
  return response.json();
}

/**
 * Create a new memo
 */
export async function createMemo(memo: MemoCreate): Promise<Memo> {
  const response = await fetch(`${API_BASE_URL}/memos/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(memo),
  });
  if (!response.ok) {
    await handleApiError(
      response,
      `Failed to create memo: ${response.statusText}`,
    );
  }
  return response.json();
}

/**
 * Update an existing memo
 */
export async function updateMemo(id: number, memo: MemoUpdate): Promise<Memo> {
  const response = await fetch(`${API_BASE_URL}/memos/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(memo),
  });
  if (!response.ok) {
    await handleApiError(
      response,
      `Failed to update memo ${id}: ${response.statusText}`,
    );
  }
  return response.json();
}

/**
 * Delete a memo
 */
export async function deleteMemo(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/memos/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    await handleApiError(
      response,
      `Failed to delete memo ${id}: ${response.statusText}`,
    );
  }
}

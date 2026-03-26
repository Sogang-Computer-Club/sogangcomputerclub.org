import type { Handle } from "@sveltejs/kit";

/**
 * SvelteKit 서버 훅 - 모든 응답에 보안 헤더 추가.
 *
 * OWASP 권장 보안 헤더:
 * - X-Content-Type-Options: MIME 스니핑 방지
 * - X-Frame-Options: 클릭재킹 방지
 * - CSP: XSS 공격 방지
 * - Permissions-Policy: 불필요한 브라우저 기능 비활성화
 */
export const handle: Handle = async ({ event, resolve }) => {
  const response = await resolve(event);

  // 보안 헤더
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-XSS-Protection", "0"); // 현대 브라우저에서는 오히려 취약점 유발 가능
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");

  // Content Security Policy
  // 'unsafe-inline': Svelte의 인라인 스타일에 필요, 프로덕션에서는 nonce 사용 권장
  response.headers.set(
    "Content-Security-Policy",
    [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self'",
      "connect-src 'self' https://www.googleapis.com", // Google Calendar API
      "frame-src 'self' https://www.youtube.com", // YouTube embeds
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join("; "),
  );

  // 브라우저 기능 제한 (카메라, 마이크, 위치 정보 비활성화)
  response.headers.set(
    "Permissions-Policy",
    "camera=(), microphone=(), geolocation=()",
  );

  return response;
};

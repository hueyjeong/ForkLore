/**
 * NextAuth.js v5 미들웨어
 * 
 * TODO: Issue #59 - 보호된 라우트 접근 제어
 * 
 * 구현 필요 사항:
 * 1. 인증이 필요한 라우트 정의
 *    - /profile
 *    - /library
 *    - /publish
 *    - /settings
 * 
 * 2. 인증되지 않은 사용자 리다이렉트
 *    - 로그인 페이지로 리다이렉트
 *    - callbackUrl 파라미터로 원래 페이지 전달
 * 
 * 3. 역 보호 (로그인된 사용자는 접근 불가)
 *    - /login, /signup (이미 로그인한 경우 홈으로 리다이렉트)
 * 
 * 참고: https://authjs.dev/getting-started/session-management/protecting
 */

// TODO: NextAuth 미들웨어 구현
// export { auth as middleware } from "@/auth"

// export const config = {
//   matcher: [
//     // 보호된 라우트
//     "/profile/:path*",
//     "/library/:path*",
//     "/publish/:path*",
//     "/settings/:path*",
//   ],
// }

export function middleware() {
  // 현재는 빈 미들웨어 (NextAuth 구현 대기)
  return;
}

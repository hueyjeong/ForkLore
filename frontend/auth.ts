/**
 * NextAuth.js v5 설정 파일
 * 
 * TODO: Issue #59 - NextAuth.js v5 설정 및 소셜 로그인 연동
 * 
 * 구현 필요 사항:
 * 1. NextAuth v5 설치 및 기본 설정
 *    - npm install next-auth@beta
 * 
 * 2. OAuth Providers 설정
 *    - Google OAuth 2.0
 *    - GitHub OAuth
 * 
 * 3. JWT 전략 설정
 *    - 백엔드 API와 연동하여 토큰 검증
 *    - Session callback에서 사용자 정보 동기화
 * 
 * 4. Credential Provider (이메일/비밀번호 로그인)
 *    - 백엔드 /api/auth/login 연동
 * 
 * 5. 환경 변수 설정 (.env.local)
 *    - NEXTAUTH_URL
 *    - NEXTAUTH_SECRET
 *    - GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET
 *    - GITHUB_ID / GITHUB_SECRET
 * 
 * 참고: https://authjs.dev/getting-started/migrating-to-v5
 */

// TODO: NextAuth 설정 구현
// import NextAuth from "next-auth"
// import Google from "next-auth/providers/google"
// import GitHub from "next-auth/providers/github"
// import Credentials from "next-auth/providers/credentials"

// export const { handlers, signIn, signOut, auth } = NextAuth({
//   providers: [
//     Google,
//     GitHub,
//     Credentials({
//       // 백엔드 API 연동
//     })
//   ],
//   callbacks: {
//     async jwt({ token, user }) {
//       // JWT 토큰 커스터마이징
//     },
//     async session({ session, token }) {
//       // 세션 데이터 커스터마이징
//     }
//   }
// })

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * 보호된 라우트 목록
 */
const PROTECTED_ROUTES = ['/profile', '/library', '/publish', '/settings'];

/**
 * 인증된 사용자는 접근 불가한 라우트 (역 보호)
 */
const AUTH_ROUTES = ['/login', '/signup'];

/**
 * 미들웨어: 인증 체크 및 리다이렉트
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // 토큰 확인
  const accessToken = request.cookies.get('access_token')?.value;
  const hasToken = !!accessToken;

  // 보호된 라우트 체크
  const isProtectedRoute = PROTECTED_ROUTES.some((route) =>
    pathname.startsWith(route)
  );

  // 인증 라우트 체크
  const isAuthRoute = AUTH_ROUTES.some((route) => pathname.startsWith(route));

  // 1. 보호된 라우트에 미인증 사용자 접근 시 로그인 페이지로 리다이렉트
  if (isProtectedRoute && !hasToken) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('callbackUrl', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // 2. 인증된 사용자가 로그인/회원가입 페이지 접근 시 홈으로 리다이렉트
  if (isAuthRoute && hasToken) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  return NextResponse.next();
}

// 미들웨어 실행 경로 설정
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};

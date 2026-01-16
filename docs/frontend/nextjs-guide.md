# ⚡ Next.js 16 가이드

**작성일**: 2026.01.16  
**작성자**: Antigravity  
**문서 버전**: v1.0

---

> ForkLore 프로젝트를 위한 Next.js 16 App Router 개발 가이드

## 1. 개요 (Overview)
Next.js 16은 React 19을 기반으로 하며, App Router 아키텍처를 더욱 성숙하게 발전시켰습니다. ForkLore 프로젝트는 서버 중심의 렌더링 전략(RSC)을 기본으로 하며, 필요한 경우에만 클라이언트 컴포넌트를 사용하여 최적의 성능과 사용자 경험을 제공합니다.

## 2. App Router 아키텍처 (Architecture)
App Router는 파일 시스템 기반 라우팅을 사용하며, `app` 디렉토리 내의 폴더 구조가 URL 경로를 결정합니다.

- **Layouts (`layout.tsx`)**: 여러 페이지 간에 공유되는 UI입니다. 상태를 유지하며 리렌더링되지 않습니다.
- **Pages (`page.tsx`)**: 해당 경로의 고유한 UI입니다.
- **Loading (`loading.tsx`)**: React Suspense를 활용한 즉각적인 로딩 UI입니다.
- **Error (`error.tsx`)**: 런타임 에러를 처리하는 클라이언트 컴포넌트입니다.
- **Route Groups (`(group)`)**: URL 경로에 영향을 주지 않고 파일을 조직화합니다.
- **Parallel Routes (`@folder`)**: 동일한 레이아웃에서 여러 페이지를 동시에 렌더링합니다.
- **Intercepting Routes (`(..)folder`)**: 현재 컨텍스트를 유지하면서 다른 경로를 로드합니다.

## 3. Server vs Client Components
Next.js 16의 핵심은 서버 컴포넌트(RSC)와 클라이언트 컴포넌트의 적절한 조화입니다.

### 결정 표 (Decision Table)

| 필요 기능 | Server Component | Client Component |
| :--- | :---: | :---: |
| 데이터 페칭 (DB 직접 접근) | ✅ | ❌ |
| 백엔드 리소스 직접 접근 (보안) | ✅ | ❌ |
| 민감한 정보 유지 (API 키 등) | ✅ | ❌ |
| 브라우저 API 사용 (window, localStorage) | ❌ | ✅ |
| 상태 및 생명주기 훅 사용 (useState, useEffect) | ❌ | ✅ |
| 사용자 상호작용 (onClick, onChange) | ❌ | ✅ |
| 커스텀 훅 (브라우저 의존성) 사용 | ❌ | ✅ |

### `'use client'` 지침
- 모든 파일은 기본적으로 서버 컴포넌트입니다.
- 상호작용이 필요한 경우에만 파일 최상단에 `'use client'`를 선언합니다.
- 클라이언트 컴포넌트는 가능한 트리의 말단(Leaf)에 배치하여 자바스크립트 번들 크기를 최소화합니다.

## 4. 데이터 페칭 패턴 (Data Fetching)
Next.js 16에서는 `fetch` API를 확장하여 캐싱 및 재검증을 제어합니다.

- **Server Actions**: 폼 제출 및 데이터 변조를 위한 비동기 함수입니다. `'use server'` 지침을 사용합니다.
- **Route Handlers**: 커스텀 요청 핸들러(GET, POST 등)를 생성합니다.
- **Caching**: `fetch(url, { cache: 'force-cache' })` 등을 통해 캐싱 전략을 세웁니다.
- **`use cache` (Experimental/Stable in 16)**: 직렬화 가능한 데이터를 캐싱하기 위한 새로운 지침입니다.

## 5. 렌더링 전략 (Rendering Strategies)
- **SSR (Server-Side Rendering)**: 요청 시마다 동적으로 렌더링합니다.
- **SSG (Static Site Generation)**: 빌드 시점에 정적으로 생성합니다.
- **ISR (Incremental Static Regeneration)**: 일정 주기마다 정적 페이지를 백그라운드에서 재생성합니다.
- **PPR (Partial Pre-Rendering)**: 정적인 셸(Shell)은 즉시 제공하고, 동적인 부분은 Suspense를 통해 비동기로 렌더링하는 혼합 전략입니다.

## 6. 메타데이터와 SEO
- **Static Metadata**: `export const metadata: Metadata = { ... }`
- **Dynamic Metadata**: `export async function generateMetadata({ params })`를 사용하여 동적으로 생성합니다.
- **Streaming**: 중요한 메타데이터는 즉시 전달되고, 나머지 본문은 스트리밍됩니다.

## 7. Next.js 16 주요 변경사항
### Async Params & searchParams
Next.js 15부터 도입되어 16에서 표준이 된 비동기 Params 처리 방식입니다.

**Migration Example:**
```tsx
// ❌ 이전 방식 (동기적 접근)
export default function Page({ params }: { params: { slug: string } }) {
  const { slug } = params;
  return <div>{slug}</div>;
}

// ✅ Next.js 16 방식 (비동기 처리)
export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <div>{slug}</div>;
}
```

### React 19 통합 포인트
- **`useFormStatus`, `useActionState`**: Server Actions와 함께 사용하여 로딩 및 에러 상태를 쉽게 관리합니다.
- **Ref as props**: 이제 `forwardRef` 없이도 `ref`를 일반 props로 전달할 수 있습니다.
- **SEO Support**: `<title>`, `<meta>`, `<link>` 태그를 컴포넌트 내 어디서든 사용할 수 있으며 자동 호이스팅됩니다.

---

## 문서 끝

# FRONTEND KNOWLEDGE BASE

**Domain:** Next.js App Router
**Path:** `frontend/`

## OVERVIEW
Server-First architecture using Next.js 16 (App Router) and React 19. We prioritize Server Components for performance and security, using Client Components only for interactivity.

## STRUCTURE
```
frontend/
├── app/            # Routes, layouts, and page components
├── components/     # UI library and feature-specific components
├── lib/            # Utilities, API clients, and Zod schemas
├── hooks/          # Custom React hooks
└── stores/         # Zustand stores for client state
```

## WHERE TO LOOK
| Component | Location | Notes |
|-----------|----------|-------|
| **Server Actions** | `app/actions.ts` | All data mutations. Validate with Zod. |
| **UI Library** | `components/ui/` | shadcn/ui components. Do not modify directly. |
| **Features** | `components/feature/` | Business-logic components (forms, lists). |
| **Stores** | `stores/` | Global client state (auth, preferences). |

## CONVENTIONS
- **Server Actions**: Use for all mutations. Validate inputs with Zod.
- **Suspense**: Wrap async data-fetching components with `<Suspense>`.
- **Shadcn**: Use standard UI components. Extend via `cn()` utility.
- **Tailwind**: Use utility classes for styling. No CSS modules.

## ANTI-PATTERNS
- ❌ **useEffect for Data**: Use Server Components or React Query/SWR instead.
- ❌ **Prop Drilling**: Use Composition or Zustand for deep state.
- ❌ **Client-Side Secrets**: Never expose API keys or secrets in client code.

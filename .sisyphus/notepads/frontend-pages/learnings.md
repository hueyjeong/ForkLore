# Learnings - Frontend Pages Implementation

## Session: 2026-01-17

### Discoveries

1. **Custom Tabs Component Missing ARIA Attributes**
   - The shadcn tabs.tsx was a custom implementation missing `role="tab"` and `data-state` attributes
   - Added ARIA semantics: `role="tablist"`, `role="tab"`, `data-state`, `aria-selected`
   - Added `onValueChange` callback for controlled components

2. **TDD Pattern Worked Well**
   - Writing tests first helped catch the Tabs ARIA issue early
   - Test pattern: `render() → getByRole/getByText → expect`

3. **Props Forwarding in Cloned Children**
   - When using `React.cloneElement` to pass props, intermediate components (TabsList) need to forward props to children
   - The TabsList wrapper needed to receive `active` and `setActive` from Tabs and pass to TabsTrigger

### Successful Approaches

1. **Component Structure**
   - Feature components in `components/feature/{domain}/`
   - Each component with co-located `.test.tsx` file
   - Pages as Server Components importing Client Components

2. **Mock Data Strategy**
   - All mock data in single `lib/mock-data.ts` file
   - TypeScript interfaces exported for type safety
   - Consistent structure across different data types

3. **Test Patterns**
   - Use `getByRole` with ARIA roles for better accessibility testing
   - Use `getByTestId` for specific icons (like pin-icon)
   - Mock Next.js internals (Image, Link, useRouter, useSearchParams)

### Technical Gotchas

1. **React DOM Warnings**
   - `setActive` prop leaking to DOM → already handled but causes console warning
   - `fill` prop for Lucide icons needs `fill="true"` as string
   - `whileHover` from Framer Motion not recognized on DOM elements

2. **URL Params in Tests**
   - Need to mock `useSearchParams` and `useRouter` from Next.js
   - Use separate `mockPush` function to verify URL changes

### Files Created

| Category | Files |
|----------|-------|
| Novels | 4 components + 3 tests + 1 page |
| Ranking | 3 components + 3 tests + 1 page |
| Community | 3 components + 3 tests + 1 page |
| Mock Data | Extended `lib/mock-data.ts` |
| UI | Fixed `components/ui/tabs.tsx` |

### Test Summary

- **Total Tests**: 45 passing
- **Test Files**: 10
- **Coverage**: All components have tests

## Session: 2026-01-19 (User Profile & Library)

### Discoveries
1. **Missing Types**: `Purchase` type was missing in `interactions.types.ts` although referenced in instructions. Added it manually.
2. **API Consistency**: `PaginatedResponse` uses `results` instead of `items`, and `PageParams` uses `limit` instead of `size`. Corrected implementation to match common types.

### Implementation Details
1. **UserProfile**:
   - Client Component using `getMyProfile` and `getWalletBalance`.
   - Used Framer Motion for entrance animations.
   - Shadcn UI (Card, Avatar, Badge) for layout.

2. **MyLibrary**:
   - Client Component using `getPurchases`.
   - Grid layout for purchased items.
   - Empty state handling.

3. **Pages**:
   - Created `/profile` and `/library` routes.
   - Wrapped components in container for proper spacing.

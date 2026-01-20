# Frontend E2E QA Plan (v1)

## Context
**Goal**: Enhance Playwright E2E tests to cover core business logic, forking mechanics, and critical user flows.
**Outcome**: Robust test suite + `backend-gap-report.md` identifying missing/broken APIs.

## Work Objectives
1. **Reorganize Test Structure**: Split `e2e` into domain-specific directories (`auth`, `reader`, `branching`, `author`, `commerce`) and implement Page Object Models.
2. **Implement Critical Scenarios**:
   - **Forking/Branching**: The core identity of ForkLore (Create Fork, Link Request, Concurrency).
   - **Context-Awareness**: Verify Wiki/Map changes based on current chapter.
   - **Commerce**: Mocked payment flow (Subscription/Point Charge).
   - **Authoring**: Editor interactions and auto-save (mocked).
3. **Document Backend Gaps**: Systematically log missing APIs in `docs/backend-gap-report.md`.

---

## Verification Strategy
- **Framework**: Playwright
- **Mocking**: Use `page.route()` ONLY for missing APIs (Payment, AI, Editor Auto-save). Enforce schemas via `mock-schemas.ts`.
- **Real Backend**: Use existing frontend dev server for Auth, Navigation, Reading (where APIs exist).
- **Helpers**: Create reusable helpers and Page Object Models (POM) for maintainability.
- **Data Cleanup**: Use API-based cleanup (`DELETE` requests) where possible; fallback to specialized "Reset State" admin endpoint if available, or manual UI teardown.

---

## Task Flow

```mermaid
graph TD
    A[Audit & Inventory] --> B[Gap Report Template]
    B --> C[POM & Helpers]
    C --> D[Reader & Context]
    C --> E[Forking & Branching]
    C --> F[Author Studio]
    C --> G[Commerce (Mocked)]
    D --> H[Negative & A11y]
    E --> H
    F --> H
    G --> H
    H --> I[Final Gap Report]
```

---

## TODOs

### 0. Discovery & Audit
- [x] **0.1 Audit Existing Tests**
  - List all current E2E specs in `frontend/tests/e2e/`.
  - **Output**: Markdown table in `docs/e2e-audit.md` (Cols: Test File | Scenarios | Gaps | Data Deps).
  - **Complete When**: All existing specs categorized.
- [x] **0.2 API Inventory**
  - Map frontend API calls to Backend Endpoints via grep.
  - **Output**: `docs/backend-gap-report.md` (initial draft with known missing endpoints).
  - **Complete When**: At least 5 known missing endpoints logged.

### 1. Setup & Documentation
- [x] **1.1 Reorganize Test Directory**
  - Create `tests/e2e/{auth,reader,branching,author,commerce,utils,pages,fixtures}`.
  - Move existing specs to appropriate folders.
  - **Note**: Current `playwright.config.ts` has incorrect `testDir`. Will be fixed in Task 1.3.
  - **Verify**: `npx playwright test` still runs (or reports expected failures).
- [x] **1.2 Create Backend Gap Report Template**
  - Create `docs/backend-gap-report.md`.
  - Structure: Critical Blockers, Partial Implementations, Data Inconsistencies.
- [x] **1.3 Test Config Update**
  - Update `playwright.config.ts`:
    - **CRITICAL**: Update `testDir` from `'./e2e'` to `'./tests/e2e'` to match actual file locations.
    - Browsers: Chromium, Firefox, Webkit.
    - Mobile: Pixel 5, iPhone 12.
    - Add `axe-playwright`.
  - **Verify**: `npx playwright test --project="Mobile Chrome"` runs.

### 2. Core Infrastructure (POM & Helpers)
- [x] **2.1 Implement Page Object Models (POM)**
  - `LoginPage`, `ReaderPage`, `NovelDetailPage`.
  - **Note**: Skip `EditorPage` as UI doesn't exist yet (see Task 3.4).
  - **Verify**: `pnpm typecheck` passes; each POM has JSDoc.
- [x] **2.2 Implement Test Helpers**
  - `tests/e2e/utils/auth-helper.ts`: `loginUser`, `logoutUser`, `getAuthToken`.
  - `tests/e2e/utils/mock-helper.ts`: Standardized mocks for Payment/AI.
  - `tests/e2e/utils/data-helper.ts`: `resetTestData` (via API calls).
  - **Verify**: Helpers export typed functions.
- [x] **2.3 Define Mock Contracts**
  - Create `tests/e2e/fixtures/mock-schemas.ts` (Zod schemas).
  - **Verify**: `mock-helper.ts` uses these schemas.

### 3. Feature Testing (Iterative)
- [x] **3.1 Auth Flow Enhancement**
  - File: `tests/e2e/auth/auth-lifecycle.spec.ts`
  - Scenarios: Login, Logout, Session Persistence, Protected Route Redirect.
  - **Gap Check**: Log any unexpected auth errors.
  - **Verify**: Tests pass in Chromium and Firefox.

- [x] **3.2 Reader & Context Awareness**
  - File: `tests/e2e/reader/context-aware.spec.ts`
  - Scenarios:
    - Read Chapter 1 → Verify Wiki Entry A is visible.
    - Read Chapter 10 → Verify Wiki Entry B is visible (timeline update).
    - Paragraph selection -> "Add Comment" button appears.
  - **Gap Check**: Verify `valid_from_chapter` logic works on frontend.
  - **Verify**: Tests pass.

- [x] **3.3 Forking & Branching (The Core)**
  - File: `tests/e2e/branching/fork-lifecycle.spec.ts`
  - Scenarios:
    - Open Chapter → Click "Fork This Branch".
    - **Modal Interaction**: Verify fork modal appears and submits.
    - **Concurrency**: Simulate multi-tab forking (race condition check).
  - **Gap Check**: Does `POST /branches` handle conflicts?
  - **Verify**: Fork creation flow passes.

- [x] **3.4 Author Studio (STUB ONLY)**
  - **Status**: Editor UI NOT IMPLEMENTED.
  - **Action**: Create `tests/e2e/author/studio.spec.ts` as a placeholder.
  - **Content**: Verify accessing `/author` shows author dashboard or appropriate placeholder (route `app/author/` exists).
  - **Gap Report**: Log "Frontend Editor UI Missing" as a critical blocker in `backend-gap-report.md`.
  - **Verify**: Stub test passes (confirming absence/placeholder).

- [x] **3.5 Commerce (Mocked)**
  - File: `tests/e2e/commerce/subscription.spec.ts`
  - Scenarios:
    - Click "Join Membership" → Mock Payment Modal → Success.
    - Verify UI updates to "Premium Member".
    - Access locked chapter.
  - **Gap Check**: Log `POST /subscriptions` as missing.
  - **Verify**: Mocked flow passes.

### 4. Robustness & Finalization
- [x] **4.1 Negative & Offline Testing**
  - File: `tests/e2e/global/resilience.spec.ts`
  - Scenarios:
    - Simulate 500 API Error → Check Error Boundary UI.
    - Simulate Network Offline → Check "Retry" button.
  - **Gap Check**: Are error states handled gracefully?
  - **Verify**: UI recovers or shows error message.

- [x] **4.2 Accessibility & Performance**
  - File: `tests/e2e/global/a11y-perf.spec.ts`
  - Scenarios:
    - Run `axe` on key pages (Home, Reader).
    - Check LCP/CLS on Novel Detail page.
  - **Thresholds**:
    - Axe: 0 Critical/Serious violations.
    - LCP: < 2.5s.
    - CLS: < 0.1.
  - **Verify**: Tests report metrics (failure optional but logged).

- [x] **4.3 Final Gap Report Population**
  - Review all `Gap Check` notes.
  - Populate `docs/backend-gap-report.md` with findings.
  - **Verify**: Report exists and contains at least 3 prioritized items.


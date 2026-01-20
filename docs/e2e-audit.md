# E2E Test Audit Report

**Date**: 2026-01-20
**Scope**: `frontend/e2e/` and `frontend/tests/e2e/`
**Purpose**: Inventory existing tests and identify critical gaps for the `frontend-qa-v1` plan.

## 📊 Summary
- **Total Specs**: 7 Files
- **Active Tests**: ~5 files with real logic (`frontend/e2e/`)
- **Stub Tests**: 2 files (`frontend/tests/e2e/`)
- **Coverage**: UI & Navigation (High), Business Logic (Low), Critical Flows (Missing)

## 📝 Detailed Inventory

| Test File | Location | Scenarios Covered | Data Dependencies | Status |
|-----------|----------|-------------------|-------------------|--------|
| `auth.spec.ts` | `frontend/e2e/` | Signup, Login, Protected Route, Middleware Redirect | Mocks `/api/auth/*` | ✅ Active (Mocked) |
| `community.spec.ts` | `frontend/e2e/` | Page visibility, Tabs, Post list, Metadata | Static/Mock data on page | ⚠️ UI Only (No Interaction) |
| `navigation.spec.ts` | `frontend/e2e/` | Home links, Layout consistency, Responsive viewports | None | ✅ Active |
| `novels.spec.ts` | `frontend/e2e/` | Category tabs, Filters, Card rendering, Detail nav | Mock data for Novels | ✅ Active |
| `ranking.spec.ts` | `frontend/e2e/` | Header, Tabs, Card list, Stats display | Mock data for Rankings | ✅ Active |
| `auth-flow.spec.ts` | `frontend/tests/e2e/` | None (Stub) | N/A | ❌ Stub |
| `reader-flow.spec.ts` | `frontend/tests/e2e/` | None (Stub) | N/A | ❌ Stub |

## 🚫 Critical Gaps

| Category | Missing Scenario | Priority |
|----------|------------------|----------|
| **Reader** | Chapter navigation, content rendering, viewer options | **P0** |
| **Forking** | Create branch, View branch tree, Link requests | **P0 (Core ID)** |
| **Context** | Wiki/Map updates based on reading progress | **P1** |
| **Author** | Studio access, Editor interaction (Stub for now) | **P1** |
| **Commerce** | Subscription flow, Coin purchase | **P2** |
| **Error** | 404/500 pages, Network offline state | **P2** |

## 💡 Recommendations

1. **Consolidate**: Move all `frontend/e2e/*.spec.ts` to `frontend/tests/e2e/` organized by domain.
2. **Deprecate Stubs**: Delete `auth-flow.spec.ts` and `reader-flow.spec.ts` in favor of robust domain tests.
3. **Enhance Auth**: Replace pure mocks with a "Real Auth" helper using the dev server if possible, or standardize mocks via Zod schemas.
4. **Implement Reader**: Create `reader/` directory and build comprehensive tests for the reading experience.

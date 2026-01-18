# Backend API Gap Report

**Last Updated**: 2026-01-19
**Context**: E2E Testing Phase (frontend-qa-v1)

## Executive Summary
This document tracks API endpoints that are missing, incomplete, or behaving unexpectedly during the Frontend E2E testing phase. It serves as a prioritized backlog for the upcoming Backend Development phase.

## 🔴 Critical Blockers (P0)
*APIs that prevent core features from working.*

| Endpoint | Feature | Issue Description | Workaround Used |
|----------|---------|-------------------|-----------------|
| `POST /subscriptions` | Membership | Payment gateway (Stripe/Toss) not integrated. | Playwright `page.route` mock |
| `POST /branches/{id}/chapters/draft` | Editor | Auto-save draft endpoint missing or undefined in spec. | None (Feature disabled) |
| `POST /wallet/charge` | Wallet | Point charging requires payment gateway. | Playwright `page.route` mock |

## 🟡 Partial / Inconsistent (P1)
*APIs that exist but lack required fields or logic.*

| Endpoint | Feature | Issue Description |
|----------|---------|-------------------|
| `GET /wiki` | Context | `valid_from_chapter` filter logic verification needed. |
| `POST /novels/{id}/branches` | Forking | Conflict handling (409) for concurrent forks needed. |

## 🟢 Minor / Optimization (P2)
*Performance issues, missing error codes, etc.*

| Endpoint | Issue | Recommendation |
|----------|-------|----------------|
| `GET /novels` | Search Performance | Add full-text search engine (ES) later. |
| `GET /users/me` | Profile | Add detailed reading stats. |

## 🧪 Test Data Requirements
*Data scenarios difficult to reproduce.*

- [ ] Need a user with `is_author=true` and 50+ published branches.
- [ ] Need a novel with circular branch references (if allowed).

## 🚧 Frontend Feature Gaps (Impacts E2E)
| Feature | Status | Test |
|---------|--------|------|
| Paragraph Comments | Missing UI | `tests/e2e/reader/context-aware.spec.ts` (Skipped) |
| Wiki Context Filtering | Not Integrated | `tests/e2e/reader/context-aware.spec.ts` (Skipped) |
| Author Editor | Missing UI | `tests/e2e/author/studio.spec.ts` (Skipped) |
| Fork Button | Missing UI | `tests/e2e/branching/fork-lifecycle.spec.ts` (Skipped) |

## 🔧 Test Infrastructure Issues
| Issue | Impact | Recommendation |
|-------|--------|----------------|
| `MockHelper` Regex | Mocks intercept page navigation (return JSON) | Add `resourceType() !== 'document'` check to all mocks. |
| Auth Selectors | Logout button detection flaky | Add `data-testid` to user menu triggers. |

# Decision: Scroll Padding for Sticky Header

## Context
The header is `sticky top-0` and changes height from `h-16` to `h-14` on scroll.
Virtuoso uses `useWindowScroll` on the `/novels` page.
Users reported content "jumping" or "padding increasing" during scroll.

## Decision
Added `scroll-pt-16` (scroll-padding-top: 4rem) to the `main` container in `frontend/app/novels/page.tsx`.

## Rationale
- Prevents layout instability when the sticky header interacts with scroll anchoring.
- Avoids modifying the shared `Header` component (which has complex state).
- Avoids global CSS changes.
- Matches the maximum height of the header (h-16), ensuring content doesn't get hidden behind it when scrolling to top.

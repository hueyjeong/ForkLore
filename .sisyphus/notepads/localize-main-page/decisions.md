# Decisions - localize-main-page

## 2026-01-16 Session: ses_437f4438cffe57HKv8i3zr74yq

### Task 1: BANNER_SLIDES Structure
- **Decision**: Use `{ id, image, link }` structure
- **Rationale**: Minimal data needed for banner carousel, reuses existing image URLs from RANKING_NOVELS
- **Trade-off**: Could have included title/description, but plan specified clean image-only banners

### Task 2: HeroSection Layout
- **Decision**: 300px fixed height with container wrapper
- **Rationale**: User specified 1/3 viewport height, 300px provides consistent experience
- **Trade-off**: Not responsive to viewport, but matches plan specification

### Task 2: Dot Indicators
- **Decision**: Simple clickable dots with white/transparent colors
- **Rationale**: Clean design, accessible with aria-labels
- **Implementation**: `onClick={() => setCurrentImageIndex(index)}`

### Task 9: Single Commit
- **Decision**: All 8 files in one commit as specified in plan
- **Rationale**: Plan explicitly stated commit at Task 9 with specific message
- **Message**: `feat: localize main page to Korean and refactor hero section`

# AGENTS: Contents App

**Module Scope:** Chapter management, Wiki systems, and Interactive Maps.
**Complexity Level:** HIGH (Versioning, Context-aware retrieval, Nested ViewSets)

## CORE ARCHITECTURE
The `contents` app manages the primary reading and supplementary materials. It uses a **Snapshot Pattern** for Wiki and Maps to ensure context-aware rendering (preventing spoilers).

### Versioning & Snapshots
- **WikiSnapshot / MapSnapshot**: Stores content valid from a specific `valid_from_chapter`.
- **Context-aware Retrieval**: APIs accept a `chapter` or `currentChapter` query parameter to return the snapshot state as of that chapter.

## VIEWSET STRUCTURE & CONVENTIONS
Due to high complexity, ViewSets are split between list/creation (nested under parent) and detail/action (referenced by ID).

### 1. Nested ViewSets (List/Create)
- `ChapterViewSet`: Nested under `/branches/{branch_id}/chapters/`.
- `WikiEntryViewSet`: Nested under `/branches/{branch_id}/wikis/`.
- `MapViewSet`: Nested under `/branches/{branch_id}/maps/`.

### 2. Detail ViewSets (Update/Delete/Actions)
- `ChapterDetailViewSet`: Handles business actions like `publish`, `schedule`, and `bookmark`.
- `WikiEntryDetailViewSet`: Handles `tags` management and context-aware retrieval.

## SERIALIZER PATTERNS
We strictly enforce serializer inheritance and specialization to maintain thin views.

- **Inheritance**: Base fields in `ModelSerializer` -> Specialized fields in `Detail` serializers.
- **MethodFields**: Used for navigation (prev/next) and context-aware snapshot injection.

## PERMISSION CLASSES
- `IsBranchAuthor`: Custom check ensuring only the creator of the `Branch` can modify its chapters, wikis, or maps.
- Public read access for published chapters; authenticated/author check for drafts.

## ANTI-PATTERNS (WATCH LIST)
- ❌ **Mega-ViewSet**: Avoid adding unrelated business logic to `ChapterDetailViewSet`. If an action exceeds 50 lines or requires complex service coordination, move it to a dedicated action view or a new ViewSet.
- ❌ **Model Logic**: Logic like Markdown-to-HTML conversion or word counting MUST reside in `services.py`, never in models or views.
- ❌ **Explicit DB Queries**: Prefer `WikiService` or `MapService` for complex lookups, especially those involving snapshot selection logic.

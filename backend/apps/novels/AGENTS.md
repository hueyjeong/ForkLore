# NOVELS KNOWLEDGE BASE

**Domain:** Core Domain (Novels & Branching)
**Path:** `backend/apps/novels/`

## OVERVIEW
The `novels` app manages the core narrative structure and the platform's signature "Forkable Story" system. It allows authors to create worlds and readers to explore or create alternative timelines through branching logic.

## KEY MODELS
- **Novel**: Central metadata for a story (Title, Genre, Status). Tracks global statistics like `linked_branch_count` and `total_view_count`.
- **Branch**: A specific timeline or narrative path. 
    - Every novel begins with one `MAIN` branch.
    - Sub-branches can be created via `fork_point_chapter`.
- **Chapter**: (Referenced from `apps.contents`) Individual episodes belonging to a specific branch. Unique per `(branch, chapter_number)`.
- **BranchLinkRequest**: A "Pull Request" for narrative branches. Allows a side branch to be officially linked to the main story.

## NARRATIVE LIFECYCLES

### Novel Creation
1. **Draft**: Initial state. Not visible publicly.
2. **Published**: Visible to readers. Requires at least one published chapter.
3. **Completed/Hiatus**: Status updates controlled by author.

### Forking (Branching)
- A reader can "Fork" a story from any chapter.
- This creates a new `Branch` with `type=SIDE`.
- The new branch inherits the world state but diverges in plot.

### Link Requests
- A side branch author can request to be "Linked" to the main novel.
- The original author reviews the request (Accept/Reject).
- Accepted branches become "Canon Divergence" or "Official AU".

## CONVENTIONS
- **Atomic Transactions**: All creation logic (`NovelService.create`, `BranchService.fork`) MUST be wrapped in `@transaction.atomic` to ensure data integrity.
- **Thin Views**: All logic resides in `services.py`. Views only parse request data and call service methods.
- **Validation**: Use `serializers.py` for input validation, but enforce business rules (e.g., "Cannot fork a private branch") in the service layer.

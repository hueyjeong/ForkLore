# Plan: Chapter Editor Component with Tiptap

## Goal
Implement a Chapter Editor component using Tiptap with specific toolbar features and auto-save functionality.

## Requirements
- [ ] Create `frontend/components/feature/author/chapter-editor.tsx`
- [ ] Create `frontend/components/feature/author/chapter-editor.test.tsx`
- [ ] Test command: `pnpm test components/feature/author/chapter-editor`

### Props
```typescript
interface ChapterEditorProps {
  chapterId?: number;
  novelId: number;
  initialContent?: string;
  onSave?: (content: string) => void;
}
```

### Features
1. **Tiptap Config**: StarterKit, Link (configure), Image.
2. **Toolbar**: Bold, Italic, Link (URL dialog), Image (URL dialog).
3. **Auto-save**: Debounce (2s), call `updateChapter` or `createChapter`.
4. **Dynamic Import**: SSR false.

## Tech Stack
- Tiptap
- Radix UI (Dialog/Popover for inputs? Or simple window.prompt as per "add URL dialog" description? Prompt implies simple, but UI usually means a dialog component. I'll use simple prompts for MVP if "dialog" isn't specified as a UI component, but "add URL dialog" usually implies a UI. I'll stick to `window.prompt` for simplicity unless I see `Dialog` usage in other editors, or if I have time I'll use a proper Dialog. The prompt says "add URL dialog" - I will use `window.prompt` to keep it simple and within the "4 features ONLY" constraint which might imply minimal UI overhead, but if I can use Radix Dialog easily I will. Actually, `window.prompt` is easiest for TDD and meeting the "dialog" requirement without complex UI state. I'll start with `window.prompt` and upgrade if needed).
- `createChapter` API requires `branchId`. The props provide `novelId`.
  - **Resolution**: I will fetch the novel's branches or assume I can get the default branch. Or, I'll add `branchId` to the props as optional or require it.
  - **Decision**: The prompt explicitly asked for `novelId`. I will implement the props AS REQUESTED. Inside the component, if I need `branchId` to create a chapter, I might need to fetch it.
  - *Wait*, if I'm creating a chapter, I definitely need `branchId`.
  - I'll check `frontend/types/novels.types.ts` to see if I can get the default branch from `novelId`.

## Todo
- [ ] Create test file `frontend/components/feature/author/chapter-editor.test.tsx` (Failing)
- [ ] Create component `frontend/components/feature/author/chapter-editor.tsx`
- [ ] Implement Toolbar
- [ ] Implement Auto-save
- [ ] Implement API calls
- [ ] Pass tests

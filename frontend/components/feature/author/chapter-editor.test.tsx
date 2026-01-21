import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { useEditor } from '@tiptap/react'
import ChapterEditor from './chapter-editor'
import * as chaptersApi from '@/lib/api/chapters.api'

// Mock the API methods
vi.mock('@/lib/api/chapters.api', () => ({
  updateChapter: vi.fn().mockResolvedValue({}),
  createChapter: vi.fn().mockResolvedValue({}),
}))

// Mock debounce to execute immediately for tests or use fake timers
// We will use fake timers in the tests
vi.useFakeTimers()

// Mock Tiptap
const mockEditor = {
  on: vi.fn(),
  off: vi.fn(),
  getHTML: vi.fn().mockReturnValue('<p>New content</p>'),
  chain: vi.fn().mockReturnThis(),
  can: vi.fn().mockReturnThis(),
  focus: vi.fn().mockReturnThis(),
  toggleBold: vi.fn().mockReturnThis(),
  toggleItalic: vi.fn().mockReturnThis(),
  setLink: vi.fn().mockReturnThis(),
  setImage: vi.fn().mockReturnThis(),
  run: vi.fn(),
  isActive: vi.fn((name: string) => false),
  isEditable: true,
}

vi.mock('@tiptap/react', () => ({
  useEditor: vi.fn(() => mockEditor),
  EditorContent: ({ editor }: { editor: any }) => <div data-testid="editor-content" />,
}))

vi.mock('@tiptap/starter-kit', () => ({
  default: {},
}))

vi.mock('@tiptap/extension-link', () => ({
  default: { configure: vi.fn() },
}))

vi.mock('@tiptap/extension-image', () => ({
  default: {},
}))

describe('ChapterEditor', () => {
  const defaultProps = {
    novelId: 1,
    chapterId: 100,
    initialContent: '<p>Initial content</p>',
    onSave: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset editor mock
    mockEditor.on.mockClear()
    mockEditor.chain.mockClear()
    mockEditor.run.mockClear()
  })

  it('mounts correctly', () => {
    render(<ChapterEditor {...defaultProps} />)
    expect(screen.getByTestId('editor-content')).toBeInTheDocument()
  })

  it('renders toolbar buttons', () => {
    render(<ChapterEditor {...defaultProps} />)
    expect(screen.getByRole('button', { name: /bold/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /italic/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /link/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /image/i })).toBeInTheDocument()
  })

  it('toggles bold when button is clicked', () => {
    render(<ChapterEditor {...defaultProps} />)
    const boldBtn = screen.getByRole('button', { name: /bold/i })
    fireEvent.click(boldBtn)
    
    expect(mockEditor.chain).toHaveBeenCalled()
    expect(mockEditor.focus).toHaveBeenCalled()
    expect(mockEditor.toggleBold).toHaveBeenCalled()
    expect(mockEditor.run).toHaveBeenCalled()
  })

  it('toggles italic when button is clicked', () => {
    render(<ChapterEditor {...defaultProps} />)
    const italicBtn = screen.getByRole('button', { name: /italic/i })
    fireEvent.click(italicBtn)
    
    expect(mockEditor.chain).toHaveBeenCalled()
    expect(mockEditor.focus).toHaveBeenCalled()
    expect(mockEditor.toggleItalic).toHaveBeenCalled()
    expect(mockEditor.run).toHaveBeenCalled()
  })

  it('triggers auto-save after typing (debounce)', async () => {
    render(<ChapterEditor {...defaultProps} />)
    
    const useEditorMock = vi.mocked(useEditor)
    const config = useEditorMock.mock.calls[0][0]
    const onUpdate = config.onUpdate
    
    expect(onUpdate).toBeDefined()
    
    // Trigger update
    act(() => {
      onUpdate({ editor: mockEditor })
    })

    // Should NOT call save immediately
    expect(chaptersApi.updateChapter).not.toHaveBeenCalled()
    expect(defaultProps.onSave).not.toHaveBeenCalled()

    // Fast forward time
    await act(async () => {
      vi.advanceTimersByTime(3000)
    })
    
    await new Promise(resolve => process.nextTick(resolve))

    expect(chaptersApi.updateChapter).toHaveBeenCalledWith(100, { content: '<p>New content</p>' })
    expect(defaultProps.onSave).toHaveBeenCalledWith('<p>New content</p>')
  })
})

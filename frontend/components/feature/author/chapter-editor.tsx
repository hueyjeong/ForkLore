'use client'

import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import { useState, useEffect, useCallback } from 'react'
import { updateChapter, createChapter } from '@/lib/api/chapters.api'
import { getBranches } from '@/lib/api/branches.api'
import { Bold, Italic, Link as LinkIcon, Image as ImageIcon, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ChapterEditorProps {
  chapterId?: number;          // undefined = new chapter
  novelId: number;
  initialContent?: string;     // HTML content
  onSave?: (content: string) => void;
}

export default function ChapterEditor({
  chapterId: initialChapterId,
  novelId,
  initialContent = '',
  onSave
}: ChapterEditorProps) {
  const [chapterId, setChapterId] = useState<number | undefined>(initialChapterId)
  const [isSaving, setIsSaving] = useState(false)
  const [lastSavedContent, setLastSavedContent] = useState(initialContent)

  const editor = useEditor({
    extensions: [
      StarterKit,
      Link.configure({ openOnClick: false }),
      Image,
    ],
    content: initialContent,
    onUpdate: ({ editor }) => {
      handleSave(editor.getHTML())
    },
    editable: true,
  })

  // Debounce logic
  const [debouncedValue, setDebouncedValue] = useState(initialContent)
  
  useEffect(() => {
    if (!editor) return
    const handler = setTimeout(() => {
      // Only save if content changed from last save
      if (debouncedValue !== lastSavedContent) {
        performSave(debouncedValue)
      }
    }, 2000)

    return () => clearTimeout(handler)
  }, [debouncedValue, lastSavedContent])

  const handleSave = (content: string) => {
    setDebouncedValue(content)
  }

  const performSave = async (content: string) => {
    setIsSaving(true)
    try {
      if (chapterId) {
        await updateChapter(chapterId, { content })
        setLastSavedContent(content)
        onSave?.(content)
      } else {
        // Need to create chapter
        // First find main branch
        // Note: In a real app we might want to let user select branch or handle this better
        const branches = await getBranches(novelId, { is_main: true })
        const mainBranch = branches.data[0]
        
        if (mainBranch) {
          const newChapter = await createChapter(mainBranch.id, {
            title: 'Untitled Chapter', // Default title
            content: content
          })
          setChapterId(newChapter.id)
          setLastSavedContent(content)
          onSave?.(content)
        } else {
          console.error('No main branch found for novel', novelId)
        }
      }
    } catch (error) {
      console.error('Failed to save chapter:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const addLink = useCallback(() => {
    if (!editor) return
    const previousUrl = editor.getAttributes('link').href
    const url = window.prompt('URL', previousUrl)

    // cancelled
    if (url === null) return

    // empty
    if (url === '') {
      editor.chain().focus().extendMarkRange('link').unsetLink().run()
      return
    }

    // update
    editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
  }, [editor])

  const addImage = useCallback(() => {
    if (!editor) return
    const url = window.prompt('Image URL')

    if (url) {
      editor.chain().focus().setImage({ src: url }).run()
    }
  }, [editor])

  if (!editor) {
    return (
      <div className="h-96 w-full animate-pulse rounded-md bg-muted/20" />
    )
  }

  return (
    <div className="flex flex-col gap-4 rounded-lg border bg-background shadow-sm">
      <div className="flex items-center gap-1 border-b p-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleBold().run()}
          disabled={!editor.can().chain().focus().toggleBold().run()}
          className={editor.isActive('bold') ? 'bg-muted' : ''}
          aria-label="Bold"
        >
          <Bold className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleItalic().run()}
          disabled={!editor.can().chain().focus().toggleItalic().run()}
          className={editor.isActive('italic') ? 'bg-muted' : ''}
          aria-label="Italic"
        >
          <Italic className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={addLink}
          className={editor.isActive('link') ? 'bg-muted' : ''}
          aria-label="Link"
        >
          <LinkIcon className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={addImage}
          aria-label="Image"
        >
          <ImageIcon className="h-4 w-4" />
        </Button>
        
        <div className="ml-auto text-xs text-muted-foreground">
          {isSaving ? (
            <span className="flex items-center gap-1">
              <Loader2 className="h-3 w-3 animate-spin" />
              Saving...
            </span>
          ) : (
            <span>{chapterId ? 'Saved' : 'Unsaved'}</span>
          )}
        </div>
      </div>
      
      <div className="min-h-[300px] p-4">
        <EditorContent editor={editor} className="prose prose-sm dark:prose-invert max-w-none focus:outline-none" />
      </div>
    </div>
  )
}

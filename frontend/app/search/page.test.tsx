import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, beforeEach, expect, it, describe } from 'vitest'
import SearchPage from './page'
import { useRouter, usePathname, useSearchParams } from 'next/navigation'

// Mock Next.js hooks
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
  usePathname: vi.fn(),
  useSearchParams: vi.fn(),
}))

vi.mock('@/components/feature/novels/novel-filters', () => ({
  NovelFilters: ({ showSearch }: any) => <div data-testid="novel-filters">{showSearch ? 'Search' : 'No Search'}</div>,
}))

vi.mock('@/components/feature/novels/infinite-novel-list', () => ({
  InfiniteNovelList: () => <div data-testid="novel-list">Novel List</div>,
}))

vi.mock('@/components/feature/search/branch-search-results', () => ({
  BranchSearchResults: ({ searchQuery }: any) => <div data-testid="branch-results">{searchQuery ? 'Branch: ' + searchQuery : 'Branch Empty'}</div>,
}))

vi.mock('@/components/feature/search/author-search-results', () => ({
  AuthorSearchResults: ({ searchQuery }: any) => <div data-testid="author-results">{searchQuery ? 'Author: ' + searchQuery : 'Author Empty'}</div>,
}))

const mockPush = vi.fn()
const mockReplace = vi.fn()

describe('SearchPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(useRouter as any).mockReturnValue({
      push: mockPush,
      replace: mockReplace,
    })
    ;(usePathname as any).mockReturnValue('/search')
  })

  it('renders search page with all tabs', () => {
    const mockSearchParams = new URLSearchParams('q=test&type=novel')
    ;(useSearchParams as any).mockReturnValue({
      get: vi.fn((key) => mockSearchParams.get(key)),
      toString: () => mockSearchParams.toString(),
    })

    render(<SearchPage />)

    expect(screen.getByText('검색')).toBeInTheDocument()
    expect(screen.getByText('원하는 작품, 브랜치, 작가를 찾아보세요.')).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: '작품' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: '브랜치' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: '작가' })).toBeInTheDocument()
  })

  it('renders with default novel type when no type in query', () => {
    const mockSearchParams = new URLSearchParams('q=test')
    ;(useSearchParams as any).mockReturnValue({
      get: vi.fn((key) => mockSearchParams.get(key) || (key === 'type' ? 'novel' : undefined)),
      toString: () => mockSearchParams.toString(),
    })

    render(<SearchPage />)

    expect(screen.getByRole('tab', { name: '작품' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: '작품' })).toHaveAttribute('data-state', 'active')
  })

  it('displays branch tab content when type is branch', async () => {
    const mockSearchParams = new URLSearchParams('q=test&type=branch')
    ;(useSearchParams as any).mockReturnValue({
      get: vi.fn((key) => mockSearchParams.get(key)),
      toString: () => mockSearchParams.toString(),
    })

    render(<SearchPage />)

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: '브랜치' })).toHaveAttribute('data-state', 'active')
      expect(screen.getByTestId('branch-results')).toHaveTextContent('Branch: test')
    })
  })

  it('displays author tab content when type is author', async () => {
    const mockSearchParams = new URLSearchParams('q=test&type=author')
    ;(useSearchParams as any).mockReturnValue({
      get: vi.fn((key) => mockSearchParams.get(key)),
      toString: () => mockSearchParams.toString(),
    })

    render(<SearchPage />)

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: '작가' })).toHaveAttribute('data-state', 'active')
      expect(screen.getByTestId('author-results')).toHaveTextContent('Author: test')
    })
  })

  it('handles tab navigation', async () => {
    const mockSearchParams = new URLSearchParams('q=test&type=novel')
    ;(useSearchParams as any).mockReturnValue({
      get: vi.fn((key) => mockSearchParams.get(key)),
      toString: () => mockSearchParams.toString(),
    })

    render(<SearchPage />)

    const branchTab = screen.getByRole('tab', { name: '브랜치' })
    fireEvent.click(branchTab)

    expect(mockPush).toHaveBeenCalledWith('/search?q=test&type=branch')
  })

  it('updates search input', () => {
    const mockSearchParams = new URLSearchParams('q=test')
    ;(useSearchParams as any).mockReturnValue({
      get: vi.fn((key) => mockSearchParams.get(key)),
      toString: () => mockSearchParams.toString(),
    })

    render(<SearchPage />)

    const input = screen.getByPlaceholderText('검색어를 입력하세요...')
    fireEvent.change(input, { target: { value: 'new search' } })

    expect(mockReplace).toHaveBeenCalledWith('/search?q=new+search')
  })
})

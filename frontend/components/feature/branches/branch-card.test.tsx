import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@/tests/utils/test-utils'
import { BranchCard } from './branch-card'
import { Branch, BranchType } from '@/types/branches.types'
import { apiClient } from '@/lib/api-client'
import { toast } from 'sonner'

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

vi.mock('sonner', () => ({
  toast: {
    error: vi.fn(),
  },
}))

const mockBranch: Branch = {
  id: 1,
  novel_id: 1,
  name: 'Test Branch',
  description: 'This is a test branch description.',
  cover_image_url: 'https://example.com/cover.jpg',
  is_main: false,
  branch_type: BranchType.MAIN,
  visibility: 'PUBLIC' as any,
  canon_status: 'NON_CANON' as any,
  parent_branch_id: null,
  fork_point_chapter: null,
  vote_count: 10,
  vote_threshold: 5,
  view_count: 100,
  chapter_count: 5,
  author: {
    id: 1,
    username: 'testuser',
    nickname: 'Test Author',
  },
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

describe('BranchCard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should render branch card with branch data', async () => {
    render(<BranchCard branch={mockBranch} />)

    await waitFor(() => {
      expect(screen.getByText('Test Branch')).toBeInTheDocument()
      expect(screen.getByText('by Test Author')).toBeInTheDocument()
      expect(screen.getByText('This is a test branch description.')).toBeInTheDocument()
      expect(screen.getByText('5')).toBeInTheDocument()
      expect(screen.getByText('10')).toBeInTheDocument()
    })
  })

  it('should render branch type badge', async () => {
    render(<BranchCard branch={mockBranch} />)

    await waitFor(() => {
      expect(screen.getByText('MAIN')).toBeInTheDocument()
    })
  })

  it('should render "No description provided" when description is empty', async () => {
    const branchWithoutDescription = { ...mockBranch, description: '' }
    render(<BranchCard branch={branchWithoutDescription} />)

    await waitFor(() => {
      expect(screen.getByText('No description provided.')).toBeInTheDocument()
    })
  })

  it('should handle vote button click', async () => {
    const mockVotedBranch = { ...mockBranch, vote_count: 11 }
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        success: true,
        data: mockVotedBranch,
        timestamp: new Date().toISOString(),
      },
    })

    render(<BranchCard branch={mockBranch} />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /vote/i })).toBeInTheDocument()
    })

    const voteButton = screen.getByRole('button', { name: /vote/i })
    fireEvent.click(voteButton)

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith('/branches/1/vote')
    })
  })

  it('should handle unvote button click', async () => {
    const mockVotedBranch = { ...mockBranch, vote_count: 9 }
    vi.mocked(apiClient.delete).mockResolvedValue({
      data: {
        success: true,
        data: mockVotedBranch,
        timestamp: new Date().toISOString(),
      },
    })

    // First vote to set isVoted to true
    render(<BranchCard branch={mockBranch} />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /vote/i })).toBeInTheDocument()
    })

    const voteButton = screen.getByRole('button', { name: /vote/i })
    fireEvent.click(voteButton)

    // Wait for vote mutation
    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith('/branches/1/vote')
    })

    // Clear previous mock
    vi.clearAllMocks()

    // Click again to unvote
    fireEvent.click(voteButton)

    await waitFor(() => {
      expect(apiClient.delete).toHaveBeenCalledWith('/branches/1/vote')
    })
  })

  it('should show error toast on vote failure', async () => {
    vi.mocked(apiClient.post).mockRejectedValue(new Error('Failed to vote'))

    render(<BranchCard branch={mockBranch} />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /vote/i })).toBeInTheDocument()
    })

    const voteButton = screen.getByRole('button', { name: /vote/i })
    fireEvent.click(voteButton)

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to update vote')
    })
  })

  it('should disable vote button during mutation', async () => {
    vi.mocked(apiClient.post).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ data: { success: true, data: mockBranch } }), 100))
    )

    render(<BranchCard branch={mockBranch} />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /vote/i })).toBeInTheDocument()
    })

    const voteButton = screen.getByRole('button', { name: /vote/i })
    fireEvent.click(voteButton)

    await waitFor(() => {
      expect(voteButton).toBeDisabled()
    })
  })
})

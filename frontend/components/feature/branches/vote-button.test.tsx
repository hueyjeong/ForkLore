import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@/tests/utils/test-utils'
import { VoteButton } from './vote-button'
import { voteBranch, unvoteBranch } from '@/lib/api/branches.api'
import { toast } from 'sonner'

vi.mock('@/lib/api/branches.api', () => ({
  voteBranch: vi.fn(),
  unvoteBranch: vi.fn(),
}))

vi.mock('sonner', () => ({
  toast: {
    error: vi.fn(),
  },
}))

const mockVoteBranch = vi.mocked(voteBranch)
const mockUnvoteBranch = vi.mocked(unvoteBranch)

describe('VoteButton', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should render vote button with initial vote count', () => {
    render(<VoteButton branchId={1} initialVoteCount={10} initialVoted={false} />)

    expect(screen.getByRole('button', { name: /vote/i })).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
  })

  it('should show voted state when initialVoted is true', () => {
    render(<VoteButton branchId={1} initialVoteCount={10} initialVoted={true} />)

    const voteButton = screen.getByRole('button', { name: /vote/i })
    expect(voteButton).toBeInTheDocument()
  })

  it('should call voteBranch when clicking vote button (not voted)', async () => {
    mockVoteBranch.mockResolvedValue({
      id: 1,
      vote_count: 11,
    } as any)

    render(<VoteButton branchId={1} initialVoteCount={10} initialVoted={false} />)

    const voteButton = screen.getByRole('button', { name: /vote/i })
    fireEvent.click(voteButton)

    await waitFor(() => {
      expect(mockVoteBranch).toHaveBeenCalledWith(1)
      expect(mockUnvoteBranch).not.toHaveBeenCalled()
    })
  })

  it('should call unvoteBranch when clicking vote button (already voted)', async () => {
    mockUnvoteBranch.mockResolvedValue({
      id: 1,
      vote_count: 9,
    } as any)

    render(<VoteButton branchId={1} initialVoteCount={10} initialVoted={true} />)

    const voteButton = screen.getByRole('button', { name: /vote/i })
    fireEvent.click(voteButton)

    await waitFor(() => {
      expect(mockUnvoteBranch).toHaveBeenCalledWith(1)
      expect(mockVoteBranch).not.toHaveBeenCalled()
    })
  })

  it('should optimistically update vote count on click', async () => {
    mockVoteBranch.mockResolvedValue({
      id: 1,
      vote_count: 11,
    } as any)

    render(<VoteButton branchId={1} initialVoteCount={10} initialVoted={false} />)

    const voteButton = screen.getByRole('button', { name: /vote/i })
    fireEvent.click(voteButton)

    // Optimistic update should happen immediately
    await waitFor(() => {
      expect(screen.getByText('11')).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(mockVoteBranch).toHaveBeenCalledWith(1)
    })
  })

  it('should optimistically revert vote count on error', async () => {
    mockVoteBranch.mockRejectedValue(new Error('Failed to vote'))

    render(<VoteButton branchId={1} initialVoteCount={10} initialVoted={false} />)

    const voteButton = screen.getByRole('button', { name: /vote/i })
    fireEvent.click(voteButton)

    await waitFor(() => {
      expect(mockVoteBranch).toHaveBeenCalledWith(1)
    })

    // Should revert back to 10 after error
    await waitFor(() => {
      expect(screen.getByText('10')).toBeInTheDocument()
    })
  })

  it('should show error toast on vote failure', async () => {
    mockVoteBranch.mockRejectedValue(new Error('Failed to vote'))

    render(<VoteButton branchId={1} initialVoteCount={10} initialVoted={false} />)

    const voteButton = screen.getByRole('button', { name: /vote/i })
    fireEvent.click(voteButton)

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to update vote')
    })
  })

  it('should call onVoteChange callback when vote changes', async () => {
    mockVoteBranch.mockResolvedValue({
      id: 1,
      vote_count: 11,
    } as any)

    const onVoteChange = vi.fn()
    render(
      <VoteButton
        branchId={1}
        initialVoteCount={10}
        initialVoted={false}
        onVoteChange={onVoteChange}
      />
    )

    const voteButton = screen.getByRole('button', { name: /vote/i })
    fireEvent.click(voteButton)

    await waitFor(() => {
      expect(onVoteChange).toHaveBeenCalledWith(true, 11)
    })

    await waitFor(() => {
      expect(mockVoteBranch).toHaveBeenCalledWith(1)
    })
  })

  it('should disable button during mutation', async () => {
    mockVoteBranch.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ id: 1 } as any), 100))
    )

    render(<VoteButton branchId={1} initialVoteCount={10} initialVoted={false} />)

    const voteButton = screen.getByRole('button', { name: /vote/i })
    fireEvent.click(voteButton)

    await waitFor(() => {
      expect(voteButton).toBeDisabled()
    })
  })
})

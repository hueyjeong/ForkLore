'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Heart } from 'lucide-react'
import { toast } from 'sonner'

import { voteBranch, unvoteBranch } from '@/lib/api/branches.api'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

export interface VoteButtonProps {
  branchId: number
  initialVoteCount: number
  initialVoted: boolean
  onVoteChange?: (voted: boolean, newCount: number) => void
}

export function VoteButton({
  branchId,
  initialVoteCount,
  initialVoted,
  onVoteChange,
}: VoteButtonProps) {
  const [voteCount, setVoteCount] = useState(initialVoteCount)
  const [isVoted, setIsVoted] = useState(initialVoted)

  const { mutate: toggleVote, isPending } = useMutation({
    mutationFn: () => (isVoted ? unvoteBranch(branchId) : voteBranch(branchId)),
    onMutate: async () => {
      // Optimistic update
      const newVoteState = !isVoted
      const newVoteCount = isVoted ? voteCount - 1 : voteCount + 1

      setIsVoted(newVoteState)
      setVoteCount(newVoteCount)

      return {
        previousVoteState: isVoted,
        previousVoteCount: voteCount,
        newVoteState,
      }
    },
    onSuccess: (data, _, context) => {
      // Sync with server response
      setVoteCount(data.vote_count)
      // Use the newVoteState from context (the state after optimistic update)
      onVoteChange?.(context?.newVoteState ?? isVoted, data.vote_count)
    },
    onError: (error, _, context) => {
      console.error('Failed to update vote for branch', branchId, error)
      toast.error('Failed to update vote')

      // Revert to previous state on error
      if (context) {
        setIsVoted(context.previousVoteState)
        setVoteCount(context.previousVoteCount)
      }
    },
  })

  return (
    <div className="flex items-center gap-1">
      <Button
        variant="ghost"
        size="icon"
        onClick={() => toggleVote()}
        disabled={isPending}
        title={isVoted ? 'Remove vote' : 'Vote for this branch'}
      >
        <Heart
          className={cn(
            'h-4 w-4 transition-colors',
            isVoted ? 'fill-red-500 text-red-500' : 'text-muted-foreground'
          )}
        />
        <span className="sr-only">{isVoted ? 'Remove vote' : 'Vote'}</span>
      </Button>
      <span className="text-sm text-muted-foreground">{voteCount}</span>
    </div>
  )
}

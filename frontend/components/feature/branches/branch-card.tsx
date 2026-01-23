"use client"

import Link from "next/link"
import { memo, useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { Heart, BookOpen, GitFork } from "lucide-react"
import { toast } from "sonner"

import { Branch, BranchType } from "@/types/branches.types"
import { voteBranch, unvoteBranch } from "@/lib/api/branches.api"
import { cn, parseViews } from "@/lib/utils"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { ForkModal } from "./fork-modal"

interface BranchCardProps {
  branch: Branch
}

export const BranchCard = memo(function BranchCard({ branch }: BranchCardProps) {
  // TODO: The API response should ideally include has_voted field.
  // For now, we'll maintain local state, defaulting to false.
  const [voteCount, setVoteCount] = useState(branch.voteCount)
  const [isVoted, setIsVoted] = useState(false)

  const { mutate: toggleVote, isPending } = useMutation({
    mutationFn: () => (isVoted ? unvoteBranch(branch.id) : voteBranch(branch.id)),
    onMutate: async () => {
      // Optimistic update
      setIsVoted((prev) => !prev)
      setVoteCount((prev) => (isVoted ? prev - 1 : prev + 1))
    },
    onError: (error) => {
      console.error('Failed to update vote for branch', branch.id, error)
      toast.error('Failed to update vote')
      // Revert on error
      setIsVoted((prev) => !prev)
      setVoteCount((prev) => (isVoted ? prev + 1 : prev - 1))
    },
  })

  const typeColors: Record<BranchType, "default" | "secondary" | "destructive" | "outline"> = {
    [BranchType.MAIN]: "default",
    [BranchType.SIDE_STORY]: "secondary",
    [BranchType.FAN_FIC]: "outline",
    [BranchType.IF_STORY]: "secondary",
  }

  return (
    <Card className="flex flex-col h-full hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex justify-between items-start gap-2">
          <div className="space-y-1">
            <CardTitle className="line-clamp-1 text-lg">
              <Link href={`/branches/${branch.id}`} className="hover:underline">
                {branch.name}
              </Link>
            </CardTitle>
            <CardDescription className="text-xs">
              by {branch.author.nickname}
            </CardDescription>
          </div>
          <Badge variant={typeColors[branch.branchType]}>
            {branch.branchType.replace("_", " ")}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1">
        <p className="text-sm text-muted-foreground line-clamp-3">
          {branch.description || "No description provided."}
        </p>
      </CardContent>
      <CardFooter className="flex justify-between items-center pt-2 border-t">
        <div className="flex gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <BookOpen className="h-4 w-4" />
            <span>{branch.chapterCount}</span>
          </div>
          <div className="flex items-center gap-1">
            <Heart className={cn("h-4 w-4", isVoted && "fill-red-500 text-red-500")} />
            <span>{parseViews(voteCount)}</span>
          </div>
        </div>
        
        <div className="flex gap-2">
           <ForkModal 
              parentBranchId={branch.id} 
              trigger={
                <Button variant="ghost" size="icon" title="Fork this branch">
                  <GitFork className="h-4 w-4" />
                </Button>
              } 
           />
           <Button
            variant="ghost"
            size="icon"
            onClick={(e) => {
              e.preventDefault()
              toggleVote()
            }}
            disabled={isPending}
          >
            <Heart
              className={cn(
                "h-4 w-4 transition-colors",
                isVoted ? "fill-red-500 text-red-500" : "text-muted-foreground"
              )}
            />
            <span className="sr-only">Vote</span>
          </Button>
        </div>
      </CardFooter>
    </Card>
  )
})

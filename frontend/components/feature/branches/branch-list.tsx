"use client"

import { useQuery } from "@tanstack/react-query"
import { Loader2, AlertCircle } from "lucide-react"

import { Branch } from "@/types/branches.types"
import { getBranches } from "@/lib/api/branches.api"
import { BranchCard } from "./branch-card"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

interface BranchListProps {
  novelId: number
}

export function BranchList({ novelId }: BranchListProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["branches", novelId],
    queryFn: () => getBranches(novelId),
  })

  if (isLoading) {
    return (
      <div className="flex h-40 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          Failed to load branches. Please try again later.
        </AlertDescription>
      </Alert>
    )
  }

  const branches = data?.results || []

  if (branches.length === 0) {
    return (
      <div className="flex h-40 items-center justify-center rounded-lg border border-dashed text-muted-foreground">
        No branches found for this novel.
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {branches.map((branch: Branch) => (
        <BranchCard key={branch.id} branch={branch} />
      ))}
    </div>
  )
}

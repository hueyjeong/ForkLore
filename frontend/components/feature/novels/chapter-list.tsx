'use client';

import React, { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getBranches } from '@/lib/api/branches.api';
import { getChapters } from '@/lib/api/chapters.api';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Branch, BranchType } from '@/types/branches.types';
import { Chapter } from '@/types/chapters.types';
import { AlertCircle } from 'lucide-react';

interface ChapterListProps {
  novelId?: number;
  branchId?: number;
}

export function ChapterList({ novelId, branchId }: ChapterListProps) {
  // 1. Fetch Branches to find the Main Branch (only if branchId is not provided)
  const { 
    data: branchesData, 
    isLoading: isBranchesLoading, 
    error: branchesError 
  } = useQuery({
    queryKey: ['branches', novelId],
    queryFn: () => getBranches(novelId!),
    enabled: !!novelId && !branchId,
  });

  // 2. Find Main Branch or use provided branchId
  const targetBranchId = useMemo(() => {
    if (branchId) return branchId;
    return branchesData?.results.find((b: Branch) => b.is_main)?.id;
  }, [branchesData, branchId]);

  // 3. Fetch Chapters for Target Branch (enabled only if targetBranchId exists)
  const { 
    data: chaptersData, 
    isLoading: isChaptersLoading, 
    error: chaptersError 
  } = useQuery({
    queryKey: ['chapters', targetBranchId],
    queryFn: () => getChapters(targetBranchId!),
    enabled: !!targetBranchId,
  });

  // Loading State
  if ((!branchId && isBranchesLoading) || (targetBranchId && isChaptersLoading)) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-center justify-between border-b p-4">
            <div className="space-y-2">
              <div className="h-4 w-48 animate-pulse bg-muted rounded" />
              <div className="h-3 w-24 animate-pulse bg-muted rounded" />
            </div>
            <div className="h-6 w-16 animate-pulse bg-muted rounded" />
          </div>
        ))}
      </div>
    );
  }

  // Error State
  if (branchesError || chaptersError) {
    return (
      <div className="p-4 border border-destructive/50 rounded-lg bg-destructive/10 text-destructive flex items-center gap-2">
        <AlertCircle className="h-4 w-4" />
        <span>Failed to load chapters. Please try again later.</span>
      </div>
    );
  }

  // No Main Branch Found (Only check if we were looking for it)
  if (!branchId && branchesData && !targetBranchId) {
     return (
      <div className="p-4 border rounded-lg bg-muted flex items-center gap-2">
        <AlertCircle className="h-4 w-4" />
        <span>No main branch found for this novel.</span>
      </div>
    );
  }

  // No Chapters Found
  if (chaptersData?.results.length === 0) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        No chapters available yet.
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card text-card-foreground shadow-sm">
      <ScrollArea className="h-[500px]">
        {chaptersData?.results.map((chapter: Chapter) => (
          <div
            key={chapter.id}
            className="flex items-center justify-between border-b p-4 last:border-0 hover:bg-muted/50 transition-colors cursor-pointer group"
          >
            <div className="flex flex-col">
              <span className="font-medium group-hover:text-primary transition-colors">
                 Chapter {chapter.chapter_number}: {chapter.title}
              </span>
              <span className="text-xs text-muted-foreground">
                {chapter.published_at ? new Date(chapter.published_at).toLocaleDateString() : 'Draft'}
              </span>
            </div>
            <div>
              {chapter.price === 0 ? (
                <Badge variant="secondary" className="bg-emerald-100 text-emerald-700 hover:bg-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400">Free</Badge>
              ) : (
                <div className="flex items-center text-sm font-semibold text-amber-500">
                  <span className="mr-1">{chapter.price}</span> 🪙
                </div>
              )}
            </div>
          </div>
        ))}
      </ScrollArea>
    </div>
  );
}

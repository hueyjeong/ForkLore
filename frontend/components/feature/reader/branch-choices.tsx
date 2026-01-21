'use client';

import { useQuery } from '@tanstack/react-query';
import { Branch } from '@/types/branches.types';
import { getBranches } from '@/lib/api/branches.api';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { GitFork, BookOpen } from 'lucide-react';
import { toast } from 'sonner';

interface BranchChoicesProps {
  novelId: number;
  currentChapterNumber: number;
}

export function BranchChoices({ novelId, currentChapterNumber }: BranchChoicesProps) {
  const { data: branches = [], isPending } = useQuery({
    queryKey: ['branches', novelId, { limit: 100 }],
    queryFn: () => getBranches(novelId, { limit: 100 }),
    select: (data) =>
      data.results.filter((b) => b.fork_point_chapter === currentChapterNumber),
  });

  if (isPending) return null;
  if (branches.length === 0) return null;

  return (
    <div className="mt-16 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex items-center gap-4">
        <Separator className="flex-1" />
        <span className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <GitFork className="h-4 w-4" />
          AVAILABLE BRANCHES
        </span>
        <Separator className="flex-1" />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {branches.map((branch) => (
          <Button
            key={branch.id}
            variant="outline"
            className="h-auto w-full flex-col items-start gap-2 whitespace-normal border-2 p-6 text-left hover:border-primary hover:bg-accent/50 transition-all duration-300 group"
            onClick={() => {
               // TODO: Navigate to the first chapter of the branch
               // or the branch details page.
               toast.info(`Selected branch: ${branch.name}`, {
                 description: "Branch navigation to be implemented" 
               });
            }}
          >
            <div className="flex w-full items-center justify-between">
              <span className="text-lg font-bold font-serif group-hover:text-primary transition-colors">
                {branch.name}
              </span>
              <span className="text-xs uppercase tracking-wider text-muted-foreground border px-2 py-0.5 rounded-full">
                {branch.branch_type}
              </span>
            </div>
            {branch.description && (
               <p className="text-sm text-muted-foreground line-clamp-2">
                 {branch.description}
               </p>
            )}
             <div className="flex items-center gap-4 text-xs text-muted-foreground mt-2">
                <span className="flex items-center gap-1">
                   <BookOpen className="h-3 w-3" />
                   {branch.chapter_count} Chapters
                </span>
             </div>
          </Button>
        ))}
      </div>
    </div>
  );
}

import React from 'react';
import Image from 'next/image';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { BookOpen, Heart, Share2, GitBranch, Eye, FileText } from 'lucide-react';
import { Branch, BranchType, CanonStatus } from '@/types/branches.types';
import { cn } from '@/lib/utils';

interface BranchDetailHeroProps {
  branch: Branch;
}

export function BranchDetailHero({ branch }: BranchDetailHeroProps) {
  return (
    <div className="relative h-[350px] w-full overflow-hidden md:h-[400px] border-b bg-muted/30">
      {/* Background Pattern/Image */}
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:60px_60px]" />
      <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-transparent" />
      
      {/* Background Image (if available) - darker and more blurred than novel hero */}
      {branch.coverImageUrl && (
        <div className="absolute inset-0 opacity-20 blur-xl">
           <Image
            src={branch.coverImageUrl}
            alt={branch.name}
            fill
            className="object-cover"
            priority
          />
        </div>
      )}

      {/* Hero Content */}
      <div className="container relative z-10 mx-auto flex h-full flex-col justify-end px-4 pb-8">
        <div className="flex flex-col md:flex-row md:items-end gap-6 md:gap-8">
          
          {/* Cover Image (smaller than novel) */}
          <div className="relative h-40 w-28 shrink-0 overflow-hidden rounded-lg shadow-xl ring-1 ring-border/50 md:h-56 md:w-40">
            <Image
              src={branch.coverImageUrl || '/placeholder-cover.jpg'}
              alt={branch.name}
              fill
              className="object-cover transition-transform hover:scale-105 duration-500"
            />
          </div>

          {/* Info */}
          <div className="flex flex-col items-start flex-1 min-w-0">
            <div className="flex flex-wrap gap-2 mb-3">
              <Badge variant={branch.isMain ? "default" : "secondary"} className="uppercase tracking-wider font-bold">
                {branch.isMain ? 'Main Branch' : branch.branchType.replaceAll('_', ' ')}
              </Badge>
              {branch.canonStatus === CanonStatus.MERGED && (
                 <Badge variant="outline" className="border-emerald-500/50 text-emerald-500 bg-emerald-500/10">
                   Canon Merged
                 </Badge>
              )}
               {branch.canonStatus === CanonStatus.CANDIDATE && (
                 <Badge variant="outline" className="border-amber-500/50 text-amber-500 bg-amber-500/10">
                   Canon Candidate
                 </Badge>
              )}
            </div>

            <h1 className="mb-2 text-2xl font-bold font-serif tracking-tight md:text-4xl lg:text-5xl text-foreground drop-shadow-sm line-clamp-2">
              {branch.name}
            </h1>
            
            <p className="mb-4 text-base text-muted-foreground font-medium flex items-center gap-2">
              <span className="text-muted-foreground/60">Branch by</span> 
              <span className="text-primary hover:underline cursor-pointer font-semibold">{branch.author.nickname}</span>
            </p>

            {/* Stats */}
            <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-muted-foreground mb-6">
              <div className="flex items-center gap-1.5" title="Total Views">
                <Eye className="h-4 w-4" />
                <span className="font-mono font-medium text-foreground">{branch.viewCount.toLocaleString()}</span>
              </div>
              <div className="flex items-center gap-1.5" title="Total Votes">
                <Heart className="h-4 w-4" />
                <span className="font-mono font-medium text-foreground">{branch.voteCount.toLocaleString()}</span>
              </div>
              <div className="flex items-center gap-1.5" title="Total Chapters">
                <FileText className="h-4 w-4" />
                <span className="font-mono font-medium text-foreground">{branch.chapterCount}</span>
              </div>
              {branch.forkPointChapter && (
                 <div className="flex items-center gap-1.5 text-xs bg-muted px-2 py-0.5 rounded-full" title="Fork Point">
                  <GitBranch className="h-3 w-3" />
                  <span>Forked at Ch. {branch.forkPointChapter}</span>
                </div>
              )}
            </div>

            <div className="flex gap-3 w-full md:w-auto">
               <Button size="lg" className="flex-1 md:flex-none shadow-lg shadow-primary/10">
                  <BookOpen className="mr-2 h-4 w-4" /> Read Branch
                </Button>
                <Button variant="outline" size="icon" className="shrink-0">
                  <Share2 className="h-4 w-4" />
                </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

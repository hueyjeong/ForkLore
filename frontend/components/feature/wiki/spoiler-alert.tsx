'use client';

import { useState } from 'react';
import { useReadingProgress } from '@/hooks/use-reading-progress';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Eye, Lock } from 'lucide-react';

interface SpoilerAlertProps {
  spoilerChapter: number;
  novelId?: number;
  children: React.ReactNode;
  className?: string;
}

export function SpoilerAlert({ 
  spoilerChapter, 
  novelId, 
  children,
  className 
}: SpoilerAlertProps) {
  const { currentChapterNumber, isLoading, error } = useReadingProgress(novelId);
  const [isRevealed, setIsRevealed] = useState(false);

  // Determination logic:
  // 1. If Loading or Error -> Protect (Safe default)
  // 2. If Not Logged In (currentChapterNumber is null) -> Show (No protection)
  // 3. If Logged In -> Check if user has reached the chapter
  
  const isLoadingOrError = isLoading || !!error;
  const isLoggedIn = currentChapterNumber !== null;

  // We protect if it's loading/error OR (we are logged in AND it's a spoiler)
  const isSpoiler = isLoggedIn && spoilerChapter > currentChapterNumber;
  const shouldProtect = isLoadingOrError || isSpoiler;
  
  // If user explicitly revealed, or logic says don't protect -> show content
  const showContent = isRevealed || !shouldProtect;

  if (showContent) {
     return <div className={cn("relative", className)}>{children}</div>;
  }

  return (
    <div className={cn("relative overflow-hidden rounded-lg border border-border/40 bg-muted/20", className)}>
       {/* Blurred Content */}
       <div 
         aria-hidden="true"
         className="select-none blur-sm opacity-50 pointer-events-none p-4 transition-all duration-300"
       >
         {children}
       </div>

       {/* Overlay */}
       <div className="absolute inset-0 flex flex-col items-center justify-center p-4 z-10 bg-background/5 backdrop-blur-[1px]">
         <div className="flex flex-col items-center gap-3 animate-in fade-in zoom-in duration-300">
            <div className="rounded-full bg-background/80 p-2 shadow-sm border border-border/50">
                <Lock className="h-4 w-4 text-muted-foreground" />
            </div>
            
            <div className="text-center space-y-0.5">
                <p className="text-sm font-semibold tracking-tight text-foreground">
                    Spoiler Alert
                </p>
                <p className="text-xs text-muted-foreground">
                    Reveals content from Chapter {spoilerChapter}
                </p>
            </div>

            <Button 
                variant="secondary" 
                size="sm" 
                onClick={() => setIsRevealed(true)}
                className="mt-1 h-8 px-4 text-xs font-medium hover:bg-primary hover:text-primary-foreground transition-colors"
            >
                <Eye className="mr-2 h-3.5 w-3.5" />
                스포일러 보기
            </Button>
         </div>
       </div>
    </div>
  );
}

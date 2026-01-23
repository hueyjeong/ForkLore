'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getWiki } from '@/lib/api/wiki.api';
import { WikiEntry, WikiSnapshot } from '@/types/wiki.types';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Loader2, Calendar, Tag, History, Image as ImageIcon } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface WikiDetailProps {
  wikiId: number;
  initialData?: WikiEntry;
}

export function WikiDetail({ wikiId, initialData }: WikiDetailProps) {
  const { data: wiki, isLoading } = useQuery({
    queryKey: ['wiki', wikiId],
    queryFn: () => getWiki(wikiId),
    initialData: initialData,
  });

  const [selectedSnapshotId, setSelectedSnapshotId] = useState<number | null>(null);

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="h-10 w-10 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!wiki) {
    return (
      <div className="flex h-96 items-center justify-center text-muted-foreground">
        Wiki entry not found.
      </div>
    );
  }

  const currentSnapshot = selectedSnapshotId
    ? wiki.snapshots.find((s) => s.id === selectedSnapshotId)
    : wiki.snapshot || wiki.snapshots[0]; // Fallback to first snapshot if current is null

  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-4">
      {/* Main Content */}
      <motion.div 
        className="lg:col-span-3 space-y-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="space-y-4">
          <div className="relative aspect-[21/9] w-full overflow-hidden rounded-xl bg-muted/50 border border-border/50 shadow-sm group">
            {wiki.image_url ? (
              <img
                src={wiki.image_url}
                alt={wiki.name}
                className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center bg-secondary/20 text-muted-foreground/30">
                <ImageIcon className="h-24 w-24" />
              </div>
            )}
             <div className="absolute inset-0 bg-gradient-to-t from-background via-background/20 to-transparent" />
             <div className="absolute bottom-6 left-6 right-6">
                <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl drop-shadow-sm">
                  {wiki.name}
                </h1>
                {wiki.first_appearance && (
                  <p className="text-sm font-medium text-muted-foreground mt-2">
                    First Appearance: Chapter {wiki.first_appearance}
                  </p>
                )}
             </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {wiki.tags.map((tag) => (
              <Badge
                key={tag.id}
                variant="secondary"
                className="px-2 py-1 text-xs font-semibold uppercase tracking-wider transition-colors hover:bg-secondary/80"
                style={{
                  backgroundColor: tag.color ? `${tag.color}20` : undefined,
                  color: tag.color,
                  borderColor: tag.color ? `${tag.color}40` : undefined,
                  borderWidth: '1px',
                  borderStyle: 'solid'
                }}
              >
                {tag.icon && <span className="mr-1.5">{tag.icon}</span>}
                {tag.name}
              </Badge>
            ))}
          </div>
        </div>

        <Separator className="my-6" />

        {/* Content */}
        <div className="prose prose-stone dark:prose-invert max-w-none">
            {currentSnapshot ? (
                <div className="whitespace-pre-wrap leading-relaxed">
                    {currentSnapshot.content}
                </div>
            ) : (
                <p className="italic text-muted-foreground">No content available.</p>
            )}
        </div>
      </motion.div>

      {/* Sidebar / Snapshots */}
      <motion.div 
        className="space-y-6 lg:border-l lg:pl-8"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <div>
          <h3 className="mb-4 flex items-center text-lg font-semibold tracking-tight">
            <History className="mr-2 h-5 w-5 text-muted-foreground" />
            History
          </h3>
          {wiki.snapshots && wiki.snapshots.length > 0 ? (
            <ScrollArea className="h-[400px] w-full rounded-md border border-border/50 bg-background/50 p-4">
              <div className="space-y-3">
                {wiki.snapshots.map((snapshot) => (
                  <button
                    key={snapshot.id}
                    onClick={() => setSelectedSnapshotId(snapshot.id)}
                    className={cn(
                      "w-full rounded-lg border p-3 text-left transition-all hover:bg-secondary/50",
                      selectedSnapshotId === snapshot.id || (!selectedSnapshotId && wiki.snapshot?.id === snapshot.id)
                        ? "border-primary/50 bg-secondary/30 ring-1 ring-primary/20"
                        : "border-border/50 bg-card/50"
                    )}
                  >
                    <div className="flex items-center justify-between mb-1">
                        <span suppressHydrationWarning className="text-xs font-medium text-muted-foreground">
                            {new Date(snapshot.createdAt).toLocaleDateString()}
                        </span>
                        {snapshot.valid_from_chapter > 0 && (
                            <Badge variant="outline" className="text-[10px] h-5 px-1.5">
                                Ch. {snapshot.valid_from_chapter}
                            </Badge>
                        )}
                    </div>
                    <div className="flex items-center text-xs text-muted-foreground/80">
                        {snapshot.contributor_type === 'AI' ? '🤖 AI Generated' : '👤 User Edit'}
                    </div>
                  </button>
                ))}
              </div>
            </ScrollArea>
          ) : (
             <div className="rounded-md border border-dashed p-4 text-center text-sm text-muted-foreground">
                No history available.
             </div>
          )}
        </div>
        
        {wiki.hidden_note && (
             <div className="rounded-md bg-yellow-500/10 p-4 border border-yellow-500/20">
                <h4 className="text-sm font-bold text-yellow-600 dark:text-yellow-400 mb-2">Hidden Note</h4>
                <p className="text-sm text-yellow-600/90 dark:text-yellow-400/90">
                    {wiki.hidden_note}
                </p>
             </div>
        )}
      </motion.div>
    </div>
  );
}

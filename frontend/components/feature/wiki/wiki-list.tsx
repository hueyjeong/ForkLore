'use client';

import { useQuery } from '@tanstack/react-query';
import { getWikis } from '@/lib/api/wiki.api';
import { WikiEntry } from '@/types/wiki.types';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Loader2, BookOpen, Tag } from 'lucide-react';
import { cn } from '@/lib/utils';

interface WikiListProps {
  branchId: number;
}

export function WikiList({ branchId }: WikiListProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['wikis', branchId],
    queryFn: () => getWikis(branchId),
  });

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-64 items-center justify-center text-destructive">
        Error loading wikis. Please try again.
      </div>
    );
  }

  const wikis = data?.results || [];

  if (wikis.length === 0) {
    return (
      <div className="flex h-64 flex-col items-center justify-center text-muted-foreground">
        <BookOpen className="mb-4 h-12 w-12 opacity-20" />
        <p>No wiki entries found for this branch.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {wikis.map((wiki, index) => (
        <WikiCard key={wiki.id} wiki={wiki} index={index} />
      ))}
    </div>
  );
}

function WikiCard({ wiki, index }: { wiki: WikiEntry; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
    >
      <Link href={`/wikis/${wiki.id}`}>
        <Card className="group h-full overflow-hidden border-border/50 bg-card/50 transition-all hover:border-primary/50 hover:bg-card hover:shadow-lg">
          <div className="aspect-video w-full overflow-hidden bg-muted/30 relative">
            {wiki.imageUrl ? (
              <img
                src={wiki.imageUrl}
                alt={wiki.name}
                className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center bg-secondary/20 text-muted-foreground/30">
                <BookOpen className="h-12 w-12" />
              </div>
            )}
            <div className="absolute inset-0 bg-gradient-to-t from-background/90 to-transparent opacity-60" />
            <div className="absolute bottom-3 left-3 right-3">
               <CardTitle className="line-clamp-1 text-lg font-bold tracking-tight text-foreground group-hover:text-primary transition-colors">
                {wiki.name}
              </CardTitle>
            </div>
          </div>
          
          <CardContent className="p-4 pt-3">
             {wiki.hiddenNote && (
                <p className="text-xs text-muted-foreground italic mb-2 line-clamp-2">
                    {wiki.hiddenNote}
                </p>
             )}
            <div className="flex flex-wrap gap-1.5">
              {wiki.tags.slice(0, 3).map((tag) => (
                <Badge 
                  key={tag.id} 
                  variant="secondary" 
                  className="px-1.5 py-0 text-[10px] font-medium tracking-wide"
                  style={{ 
                    backgroundColor: tag.color ? `${tag.color}20` : undefined,
                    color: tag.color,
                    borderColor: tag.color ? `${tag.color}40` : undefined,
                  }}
                >
                  {tag.icon && <span className="mr-1">{tag.icon}</span>}
                  {tag.name}
                </Badge>
              ))}
              {wiki.tags.length > 3 && (
                <Badge variant="outline" className="px-1.5 py-0 text-[10px]">
                  +{wiki.tags.length - 3}
                </Badge>
              )}
            </div>
          </CardContent>
          <CardFooter className="p-4 pt-0 text-xs text-muted-foreground flex justify-between items-center">
             <span>First appearance: Ch. {wiki.firstAppearance ?? '-'}</span>
          </CardFooter>
        </Card>
      </Link>
    </motion.div>
  );
}

'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getWikiTags } from '@/lib/api/wiki.api';
import { WikiList } from '@/components/feature/wiki/wiki-list';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface WikisViewProps {
  branchId: number;
}

export function WikisView({ branchId }: WikisViewProps) {
  const [search, setSearch] = useState('');
  const [selectedTagId, setSelectedTagId] = useState<number | null>(null);

  const { data: tags, isLoading: isTagsLoading } = useQuery({
    queryKey: ['wiki-tags', branchId],
    queryFn: () => getWikiTags(branchId),
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search wikis..."
            className="pl-9"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-medium text-muted-foreground">Filter by tag</h3>
        <div className="flex flex-wrap gap-2">
          <Badge
            variant={selectedTagId === null ? "default" : "outline"}
            className="cursor-pointer hover:bg-primary/90"
            onClick={() => setSelectedTagId(null)}
          >
            All
          </Badge>
          
          {isTagsLoading ? (
             <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          ) : (
            tags?.map((tag) => (
              <Badge
                key={tag.id}
                variant={selectedTagId === tag.id ? "secondary" : "outline"}
                className={cn(
                  "cursor-pointer transition-all",
                  selectedTagId === tag.id && "ring-1 ring-primary"
                )}
                style={{
                  backgroundColor: selectedTagId === tag.id && tag.color ? `${tag.color}20` : undefined,
                  color: tag.color || undefined,
                  borderColor: tag.color ? `${tag.color}40` : undefined,
                }}
                onClick={() => setSelectedTagId(selectedTagId === tag.id ? null : tag.id)}
              >
                {tag.icon && <span className="mr-1">{tag.icon}</span>}
                {tag.name}
              </Badge>
            ))
          )}
        </div>
      </div>

      <WikiList 
        branchId={branchId} 
        search={search} 
        tagId={selectedTagId} 
      />
    </div>
  );
}

'use client';

import { useState, useMemo, useCallback } from 'react';
import { Virtuoso } from 'react-virtuoso';
import { NovelGrid } from './novel-grid';
import { NOVELS_LIST, type Novel } from '@/lib/mock-data';

const ITEMS_PER_PAGE = 12;

interface InfiniteNovelListProps {
  genre?: string;
  status?: string;
  sort?: 'popular' | 'latest';
  searchQuery?: string;
}

function parseViews(views: string): number {
  const num = parseFloat(views);
  if (views.includes('M')) return num * 1000000;
  if (views.includes('K')) return num * 1000;
  return num;
}

export function InfiniteNovelList({ 
  genre, 
  status, 
  sort = 'popular',
  searchQuery 
}: InfiniteNovelListProps) {
  const [loadedCount, setLoadedCount] = useState(ITEMS_PER_PAGE);

  const filteredNovels = useMemo(() => {
    let result = [...NOVELS_LIST];

    if (genre && genre !== '전체') {
      result = result.filter(novel => novel.genre === genre);
    }

    if (status && status !== '전체') {
      result = result.filter(novel => novel.status === status);
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(novel => 
        novel.title.toLowerCase().includes(query) ||
        novel.author.toLowerCase().includes(query)
      );
    }

    if (sort === 'popular') {
      result.sort((a, b) => parseViews(b.views) - parseViews(a.views));
    } else if (sort === 'latest') {
      result.sort((a, b) => 
        new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime()
      );
    }

    return result;
  }, [genre, status, sort, searchQuery]);

  const displayedNovels = useMemo(() => {
    return filteredNovels.slice(0, loadedCount);
  }, [filteredNovels, loadedCount]);

  const loadMore = useCallback(() => {
    if (loadedCount < filteredNovels.length) {
      setLoadedCount(prev => Math.min(prev + ITEMS_PER_PAGE, filteredNovels.length));
    }
  }, [loadedCount, filteredNovels.length]);

  if (filteredNovels.length === 0) {
    return (
      <div className="flex items-center justify-center py-20 text-muted-foreground">
        표시할 작품이 없습니다
      </div>
    );
  }

  return (
    <Virtuoso
      useWindowScroll
      data={displayedNovels}
      endReached={loadMore}
      overscan={200}
      itemContent={(index, novel) => (
        <div className="mb-4">
          <NovelGrid novels={[novel]} />
        </div>
      )}
      components={{
        List: ({ children, ...props }) => (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4" {...props}>
            {children}
          </div>
        ),
        Item: ({ children, ...props }) => (
          <div {...props}>{children}</div>
        ),
      }}
    />
  );
}

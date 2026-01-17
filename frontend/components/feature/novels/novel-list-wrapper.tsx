'use client';

import { useSearchParams } from 'next/navigation';
import { InfiniteNovelList } from '@/components/feature/novels/infinite-novel-list';

export function NovelListWrapper() {
  const searchParams = useSearchParams();
  
  const genre = searchParams.get('genre') || undefined;
  const status = searchParams.get('status') || undefined;
  const category = searchParams.get('category') || '전체';
  const sort = (searchParams.get('sort') as 'popular' | 'latest') || 'popular';
  const searchQuery = searchParams.get('q') || undefined;

  return (
    <InfiniteNovelList
      genre={genre}
      status={status}
      category={category}
      sort={sort}
      searchQuery={searchQuery}
    />
  );
}

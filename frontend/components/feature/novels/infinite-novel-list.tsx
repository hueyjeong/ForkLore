'use client';

import { useMemo } from 'react';
import { Virtuoso } from 'react-virtuoso';
import { useInfiniteQuery } from '@tanstack/react-query';
import { NovelpiaCard } from './novelpia-card';
import { getNovels } from '@/lib/api/novels.api';
import { Genre, NovelStatus, NovelListParams } from '@/types/novels.types';
import { Loader2 } from 'lucide-react';

interface InfiniteNovelListProps {
  genre?: string;
  status?: string;
  category?: string;
  sort?: 'popular' | 'latest';
  searchQuery?: string;
}

const genreMap: Record<string, Genre> = {
  '판타지': Genre.FANTASY,
  '로맨스': Genre.ROMANCE,
  '무협': Genre.MARTIAL,
  'SF': Genre.SF,
  '스릴러': Genre.THRILLER,
  '미스터리': Genre.MYSTERY,
  '역사': Genre.HISTORY,
  '현대': Genre.MODERN,
  '게임': Genre.GAME,
};

const statusMap: Record<string, NovelStatus> = {
  '연재중': NovelStatus.ONGOING,
  '완결': NovelStatus.COMPLETED,
  '휴재': NovelStatus.HIATUS,
};

export function InfiniteNovelList({ 
  genre, 
  status, 
  category,
  sort = 'popular',
  searchQuery 
}: InfiniteNovelListProps) {
  
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError
  } = useInfiniteQuery({
    queryKey: ['novels', genre, status, category, sort, searchQuery],
    queryFn: async ({ pageParam = 1 }) => {
      const params: NovelListParams = {
        page: pageParam,
        size: 12,
      };

      if (genre && genre !== '전체') {
        const mappedGenre = genreMap[genre];
        if (mappedGenre) params.genre = mappedGenre;
      }

      if (status && status !== '전체') {
        const mappedStatus = statusMap[status];
        if (mappedStatus) params.status = mappedStatus;
      }

      if (category && category !== '전체') {
        switch (category) {
          case '멤버십':
            params.isPremium = true;
            break;
          case '독점':
            params.isExclusive = true;
            break;
          case '완결':
            params.status = NovelStatus.COMPLETED;
            break;
          case '신작':
            break;
        }
      }

      if (searchQuery) {
        params.search = searchQuery;
      }

      if (category === '신작') {
        params.sort = 'createdAt';
        params.order = 'desc';
      } else if (sort === 'popular') {
        params.sort = 'totalViewCount';
        params.order = 'desc';
      } else if (sort === 'latest') {
        params.sort = 'createdAt';
        params.order = 'desc';
      }

      return getNovels(params);
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (!lastPage.next) return undefined;
      const url = new URL(lastPage.next);
      const page = url.searchParams.get('page');
      return page ? parseInt(page, 10) : undefined;
    },
  });

  const novels = useMemo(() => {
    const result = data?.pages.flatMap((page) => page.results) || [];
    console.log('[InfiniteNovelList] Novels:', result.length, 'Loading:', isLoading, 'Error:', isError);
    return result;
  }, [data, isLoading, isError]);

  console.log('[InfiniteNovelList] Render state:', { 
    novelsCount: novels.length, 
    isLoading, 
    isError,
    pagesCount: data?.pages?.length 
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center py-20 text-red-500">
        데이터를 불러오는 중 오류가 발생했습니다.
      </div>
    );
  }

  if (novels.length === 0) {
    return (
      <div className="flex items-center justify-center py-20 text-muted-foreground">
        표시할 작품이 없습니다
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {novels.map((novel) => (
          <div key={novel.id}>
            <NovelpiaCard novel={novel} />
          </div>
        ))}
      </div>
      
      {hasNextPage && (
        <div className="flex justify-center mt-8">
          <button
            onClick={() => fetchNextPage()}
            disabled={isFetchingNextPage}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
          >
            {isFetchingNextPage ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              '더 보기'
            )}
          </button>
        </div>
      )}
    </>
  );
}

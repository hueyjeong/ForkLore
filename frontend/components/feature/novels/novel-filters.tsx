'use client';

import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import { useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area';
import { Search } from 'lucide-react';

const GENRES = ['전체', '판타지', '로맨스', '무협', 'SF', '미스터리'];
const STATUSES = ['전체', '연재중', '완결'];
const SORT_OPTIONS = [
  { value: 'popular', label: '인기순' },
  { value: 'latest', label: '최신순' },
];

export function NovelFilters() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const currentGenre = searchParams.get('genre') || '전체';
  const currentStatus = searchParams.get('status') || '전체';
  const currentSort = searchParams.get('sort') || 'popular';
  const currentSearch = searchParams.get('q') || '';

  const updateParams = useCallback(
    (key: string, value: string) => {
      const params = new URLSearchParams(searchParams.toString());
      
      if (value === '전체' || value === '') {
        params.delete(key);
      } else {
        params.set(key, value);
      }

      const queryString = params.toString();
      router.push(queryString ? `${pathname}?${queryString}` : pathname);
    },
    [router, pathname, searchParams]
  );

  const handleSearch = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      updateParams('q', e.target.value);
    },
    [updateParams]
  );

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="작품 검색..."
          className="pl-10"
          defaultValue={currentSearch}
          onChange={handleSearch}
        />
      </div>

      {/* Genre Filter */}
      <ScrollArea className="w-full whitespace-nowrap">
        <div className="flex w-max space-x-2 pb-2">
          {GENRES.map((genre) => (
            <Button
              key={genre}
              variant={currentGenre === genre ? 'default' : 'outline'}
              size="sm"
              onClick={() => updateParams('genre', genre)}
              className="rounded-full px-4 font-medium"
            >
              {genre}
            </Button>
          ))}
        </div>
        <ScrollBar />
      </ScrollArea>

      {/* Status Filter and Sort */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex gap-2">
          {STATUSES.map((status) => (
            <Button
              key={status}
              variant={currentStatus === status ? 'default' : 'outline'}
              size="sm"
              onClick={() => updateParams('status', status)}
              className="rounded-full px-4 font-medium"
            >
              {status}
            </Button>
          ))}
        </div>

        <Select
          value={currentSort}
          onValueChange={(value) => updateParams('sort', value)}
        >
          <SelectTrigger className="w-[120px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {SORT_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}

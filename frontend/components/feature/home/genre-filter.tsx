'use client';

import React from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area';

const GENRE_MAP: Record<string, string> = {
  '전체': '',
  '판타지': 'FANTASY',
  '로맨스': 'ROMANCE',
  'SF': 'SCIFI',
  '미스터리': 'MYSTERY',
  '호러': 'HORROR',
  '스릴러': 'THRILLER',
  '역사': 'HISTORICAL',
  '액션': 'ACTION',
  '어드벤처': 'ADVENTURE',
  '코미디': 'COMEDY',
  '드라마': 'DRAMA',
};

const GENRES = Object.keys(GENRE_MAP);

export function GenreFilter() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const currentGenre = searchParams.get('genre') || '';
  
  const activeGenre = Object.entries(GENRE_MAP).find(([_, value]) => value === currentGenre)?.[0] || '전체';

  const handleGenreClick = (genre: string) => {
    const genreValue = GENRE_MAP[genre];
    const params = new URLSearchParams(searchParams.toString());
    
    if (genreValue) {
      params.set('genre', genreValue);
    } else {
      params.delete('genre');
    }
    
    router.push(`/?${params.toString()}`, { scroll: false });
  };

  return (
    <div className="sticky top-[60px] z-30 w-full bg-background/95 py-2 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
      <ScrollArea className="w-full whitespace-nowrap px-4">
        <div className="flex w-max space-x-2 pb-2 pt-1">
          {GENRES.map((genre) => (
            <Button
              key={genre}
              variant={activeGenre === genre ? "default" : "outline"}
              size="sm"
              onClick={() => handleGenreClick(genre)}
              className="rounded-full px-4 font-medium transition-all"
            >
              {genre}
            </Button>
          ))}
        </div>
        <ScrollBar />
      </ScrollArea>
    </div>
  );
}

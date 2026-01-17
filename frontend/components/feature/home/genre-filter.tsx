'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area';

const GENRES = [
  '전체',
  '판타지',
  '로맨스',
  'SF',
  '미스터리',
  '호러',
  '스릴러',
  '역사',
  '액션',
  '어드벤처',
  '코미디',
  '드라마',
];

export function GenreFilter() {
  const [activeGenre, setActiveGenre] = React.useState('전체');

  return (
    <div className="sticky top-[60px] z-30 w-full bg-background/95 py-2 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
      <ScrollArea className="w-full whitespace-nowrap px-4">
        <div className="flex w-max space-x-2 pb-2 pt-1">
          {GENRES.map((genre) => (
            <Button
              key={genre}
              variant={activeGenre === genre ? "default" : "outline"}
              size="sm"
              onClick={() => setActiveGenre(genre)}
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

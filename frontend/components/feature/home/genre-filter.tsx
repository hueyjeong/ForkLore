'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area';

const GENRES = [
  'All',
  'Fantasy',
  'Romance',
  'Sci-Fi',
  'Mystery',
  'Horror',
  'Thriller',
  'Historical',
  'Action',
  'Adventure',
  'Comedy',
  'Drama',
];

export function GenreFilter() {
  const [activeGenre, setActiveGenre] = React.useState('All');

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
        <ScrollBar orientation="horizontal" className="invisible" />
      </ScrollArea>
    </div>
  );
}

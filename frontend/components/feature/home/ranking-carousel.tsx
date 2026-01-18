'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { ChevronRight, Trophy, Star } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area';
import { RANKING_NOVELS } from '@/lib/mock-data';

export function RankingCarousel() {
  return (
    <div className="w-full space-y-4 py-8">
      <div className="flex items-center justify-between px-4">
        <h2 className="flex items-center text-2xl font-bold font-serif tracking-tight">
          <Trophy className="mr-2 h-6 w-6 text-yellow-500" />
          인기 랭킹
        </h2>
        <Link href="/rankings" className="flex items-center text-sm font-medium text-muted-foreground hover:text-primary">
          전체보기 <ChevronRight className="ml-1 h-4 w-4" />
        </Link>
      </div>

      <ScrollArea className="w-full whitespace-nowrap px-4">
        <div className="flex w-max space-x-4 pb-4">
          {RANKING_NOVELS.map((novel, index) => (
            <Link key={novel.id} href={`/novels/${novel.id}`} className="group relative block w-[160px] md:w-[200px]">
              {/* Rank Badge */}
              <div className="absolute -left-2 -top-2 z-10 flex h-10 w-10 items-center justify-center rounded-full bg-background font-bold shadow-lg ring-2 ring-primary/20">
                <span className={`text-lg ${index < 3 ? 'text-yellow-500' : 'text-muted-foreground'}`}>
                  {index + 1}
                </span>
              </div>

              {/* Cover */}
              <div className="overflow-hidden rounded-xl shadow-md transition-transform duration-300 group-hover:-translate-y-1 group-hover:shadow-xl">
                <div className="relative aspect-[2/3] w-full">
                  <Image
                    src={novel.coverUrl}
                    alt={novel.title}
                    fill
                    className="object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                </div>
              </div>

              {/* Info */}
              <div className="mt-3 space-y-1 whitespace-normal">
                <h3 className="line-clamp-2 text-base font-semibold leading-tight group-hover:text-primary transition-colors">
                  {novel.title}
                </h3>
                <p className="text-xs text-muted-foreground">{novel.author}</p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>👁️ {novel.views}</span>
                  <span className="flex items-center text-yellow-500">★ {novel.rating}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
        <ScrollBar />
      </ScrollArea>
    </div>
  );
}

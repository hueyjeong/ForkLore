'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Star, ThumbsUp } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { getNovels } from '@/lib/api/novels.api';
import { Novel, Genre } from '@/types/novels.types';

interface RecommendationListProps {
  genre?: string;
}

export function RecommendationList({ genre }: RecommendationListProps) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['novels', 'recommendation', genre],
    queryFn: () => {
      const params = { 
        size: 6, 
        sort: 'created_at',
        ...(genre && { genre: genre as Genre })
      };
      return getNovels(params);
    },
  });

  const novels = data?.results || [];

  if (isLoading) {
    return (
      <div className="space-y-6 py-8">
        <div className="px-4">
          <div className="h-8 w-48 animate-pulse rounded bg-muted" />
          <div className="mt-2 h-4 w-64 animate-pulse rounded bg-muted" />
        </div>
        <div className="grid gap-4 px-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="flex h-[160px] animate-pulse overflow-hidden rounded-xl border border-muted bg-card">
              <div className="w-32 shrink-0 bg-muted" />
              <div className="flex flex-1 flex-col justify-between p-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <div className="h-5 w-3/4 rounded bg-muted" />
                    <div className="h-4 w-8 rounded bg-muted" />
                  </div>
                  <div className="h-3 w-full rounded bg-muted" />
                  <div className="h-3 w-2/3 rounded bg-muted" />
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex gap-1">
                    <div className="h-5 w-12 rounded bg-muted" />
                    <div className="h-5 w-12 rounded bg-muted" />
                  </div>
                  <div className="h-3 w-16 rounded bg-muted" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return null;
  }

  return (
    <div className="space-y-6 py-8">
      <div className="px-4">
        <h2 className="text-2xl font-bold font-serif tracking-tight">맞춤 추천</h2>
        <p className="text-muted-foreground">읽은 작품을 기반으로 추천합니다</p>
      </div>

      <div className="grid gap-4 px-4 md:grid-cols-2 lg:grid-cols-3">
        {novels.map((novel: Novel) => (
          <Link key={novel.id} href={`/novels/${novel.id}`} className="group">
            <Card className="h-full overflow-hidden border-muted bg-card transition-all hover:border-primary/50 hover:shadow-md">
              <div className="flex h-full">
                {/* Image */}
                <div className="relative w-32 shrink-0 bg-muted">
                  {novel.coverImageUrl ? (
                    <Image
                      src={novel.coverImageUrl}
                      alt={novel.title}
                      fill
                      className="object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center text-muted-foreground text-xs">
                      No Image
                    </div>
                  )}
                </div>
                
                {/* Content */}
                <div className="flex flex-1 flex-col justify-between p-4">
                  <div className="space-y-2">
                    <div className="flex items-start justify-between">
                      <h3 className="line-clamp-2 font-semibold leading-tight group-hover:text-primary transition-colors">
                        {novel.title}
                      </h3>
                      <div className="flex items-center text-xs font-medium text-yellow-500">
                        <ThumbsUp className="mr-1 h-3 w-3 fill-current" />
                        {(novel.totalLikeCount ?? 0).toLocaleString()}
                      </div>
                    </div>
                    <p className="line-clamp-2 text-xs text-muted-foreground">
                      {novel.description}
                    </p>
                  </div>
                  
                  <div className="mt-4 flex items-center justify-between">
                    <div className="flex gap-1">
                      <Badge variant="secondary" className="px-1.5 py-0 text-[10px]">
                        {novel.genre}
                      </Badge>
                      <Badge variant="outline" className="px-1.5 py-0 text-[10px]">
                        {novel.status}
                      </Badge>
                    </div>
                    <p className="text-[10px] text-muted-foreground">
                      {novel.author.nickname}
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}

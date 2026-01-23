import React from 'react';
import Image from 'next/image';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { BookOpen, Heart, Share2 } from 'lucide-react';
import { Novel } from '@/types/novels.types';

interface NovelDetailHeroProps {
  novel: Novel;
}

export function NovelDetailHero({ novel }: NovelDetailHeroProps) {
  return (
    <div className="relative h-[400px] w-full overflow-hidden md:h-[500px]">
      {/* Background Image with Blur */}
      <div className="absolute inset-0">
        <Image
          src={novel.coverImageUrl || '/placeholder-cover.jpg'}
          alt={novel.title}
          fill
          className="object-cover opacity-60 blur-sm"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-transparent" />
      </div>

      {/* Hero Content */}
      <div className="container relative z-10 mx-auto flex h-full flex-col items-center justify-end px-4 pb-8 text-center md:flex-row md:items-end md:justify-start md:text-left">
        {/* Cover Image */}
        <div className="relative mb-4 h-48 w-32 shrink-0 overflow-hidden rounded-lg shadow-2xl md:mb-0 md:mr-8 md:h-72 md:w-48">
          <Image
            src={novel.coverImageUrl || '/placeholder-cover.jpg'}
            alt={novel.title}
            fill
            className="object-cover"
          />
        </div>

        {/* Info */}
        <div className="flex flex-col items-center md:items-start">
          <Badge variant="secondary" className="mb-2 w-fit">
            {novel.status}
          </Badge>
          <h1 className="mb-2 text-3xl font-bold font-serif tracking-tight md:text-5xl lg:text-6xl text-foreground drop-shadow-md">
            {novel.title}
          </h1>
          <p className="mb-4 text-lg text-muted-foreground font-medium">
            by <span className="text-primary hover:underline cursor-pointer">{novel.author.nickname}</span>
          </p>

          {/* Stats */}
          <div className="mb-6 flex space-x-6 text-sm md:text-base">
            <div className="flex flex-col items-center md:items-start">
              <span className="font-bold text-foreground">{novel.totalViewCount.toLocaleString()}</span>
              <span className="text-xs text-muted-foreground uppercase tracking-wider">Reads</span>
            </div>
            <div className="flex flex-col items-center md:items-start">
              <span className="font-bold text-foreground">{novel.totalLikeCount.toLocaleString()}</span>
              <span className="text-xs text-muted-foreground uppercase tracking-wider">Likes</span>
            </div>
            {/* Rating is not in the Novel interface, omitting or assuming it might be added later or calculated */}
            {/* <div className="flex flex-col items-center md:items-start">
                <span className="font-bold text-foreground">★ {novel.rating}</span>
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Rating</span>
              </div> */}
             <div className="flex flex-col items-center md:items-start">
              <span className="font-bold text-foreground">{novel.totalChapterCount}</span>
              <span className="text-xs text-muted-foreground uppercase tracking-wider">Chapters</span>
            </div>
          </div>

          {/* Actions (Desktop) */}
          <div className="hidden gap-3 md:flex">
            <Button size="lg" className="px-8 font-semibold shadow-lg shadow-primary/20">
              <BookOpen className="mr-2 h-5 w-5" /> Read First Chapter
            </Button>
            <Button size="icon" variant="outline" className="rounded-full bg-background/50 backdrop-blur-md border-white/20 hover:bg-background/80">
              <Heart className="h-5 w-5" />
            </Button>
            <Button size="icon" variant="outline" className="rounded-full bg-background/50 backdrop-blur-md border-white/20 hover:bg-background/80">
              <Share2 className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

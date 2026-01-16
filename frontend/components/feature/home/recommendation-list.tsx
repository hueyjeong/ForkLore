'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Star, Clock } from 'lucide-react';

const RECOMMENDATIONS = [
  { 
    id: 101, 
    title: 'Beneath the Digital Sky', 
    author: 'CyberPunk', 
    desc: 'In a future where memories can be uploaded, a detective searches for the missing fragment of a dead politician.',
    tags: ['Sci-Fi', 'Mystery'],
    rating: 4.5,
    cover: 'https://images.unsplash.com/photo-1515630278258-407f66498911?q=80&w=2998&auto=format&fit=crop'
  },
  { 
    id: 102, 
    title: 'The Herbalist\'s Apprentice', 
    author: 'GreenThumb', 
    desc: 'She thought she was just picking flowers, until the flowers started whispering back.',
    tags: ['Fantasy', 'Slice of Life'],
    rating: 4.9,
    cover: 'https://images.unsplash.com/photo-1470813740244-df37b8c1edcb?q=80&w=2942&auto=format&fit=crop'
  },
  { 
    id: 103, 
    title: 'Code: Breaker', 
    author: 'NullPointer', 
    desc: 'The game was supposed to be unbeatable. He found a glitch that changed reality.',
    tags: ['Action', 'LitRPG'],
    rating: 4.2,
    cover: 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=2940&auto=format&fit=crop'
  },
];

export function RecommendationList() {
  return (
    <div className="space-y-6 py-8">
      <div className="px-4">
        <h2 className="text-2xl font-bold font-serif tracking-tight">Picked for You</h2>
        <p className="text-muted-foreground">Based on your reading history</p>
      </div>

      <div className="grid gap-4 px-4 md:grid-cols-2 lg:grid-cols-3">
        {RECOMMENDATIONS.map((novel) => (
          <Link key={novel.id} href={`/novels/${novel.id}`} className="group">
            <Card className="h-full overflow-hidden border-muted bg-card transition-all hover:border-primary/50 hover:shadow-md">
              <div className="flex h-full">
                {/* Image */}
                <div className="relative w-32 shrink-0">
                  <Image
                    src={novel.cover}
                    alt={novel.title}
                    fill
                    className="object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                </div>
                
                {/* Content */}
                <div className="flex flex-1 flex-col justify-between p-4">
                  <div className="space-y-2">
                    <div className="flex items-start justify-between">
                      <h3 className="line-clamp-2 font-semibold leading-tight group-hover:text-primary transition-colors">
                        {novel.title}
                      </h3>
                      <div className="flex items-center text-xs font-medium text-yellow-500">
                        <Star className="mr-1 h-3 w-3 fill-current" />
                        {novel.rating}
                      </div>
                    </div>
                    <p className="line-clamp-2 text-xs text-muted-foreground">
                      {novel.desc}
                    </p>
                  </div>
                  
                  <div className="mt-4 flex items-center justify-between">
                    <div className="flex gap-1">
                      {novel.tags.map(tag => (
                        <Badge key={tag} variant="secondary" className="px-1.5 py-0 text-[10px]">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                    <p className="text-[10px] text-muted-foreground">
                      by {novel.author}
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

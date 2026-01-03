'use client';

import Image from 'next/image';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Star } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface NovelCardProps {
  id: string;
  title: string;
  author: string;
  coverUrl: string;
  genre: string;
  rating: number;
  className?: string;
}

export function NovelCard({ id, title, author, coverUrl, genre, rating, className }: NovelCardProps) {
  return (
    <motion.div
      whileHover={{ y: -8 }}
      className={cn("group relative flex flex-col gap-3", className)}
    >
      <Link href={`/novels/${id}`} className="relative aspect-[3/4] overflow-hidden rounded-xl shadow-md transition-all group-hover:shadow-2xl group-hover:shadow-primary/10">
        <Image
          src={coverUrl}
          alt={title}
          fill
          className="object-cover transition-transform duration-500 group-hover:scale-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        
        <Badge className="absolute top-3 left-3 glass border-white/20 text-white font-medium">
          {genre}
        </Badge>
      </Link>
      
      <div className="flex flex-col gap-1 px-1">
        <h3 className="font-serif font-bold text-lg leading-tight line-clamp-1 text-premium group-hover:text-primary transition-colors">
          {title}
        </h3>
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground line-clamp-1">{author}</span>
          <div className="flex items-center gap-1 text-primary">
            <Star className="w-3.5 h-3.5 fill-current" />
            <span className="font-semibold">{rating.toFixed(1)}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

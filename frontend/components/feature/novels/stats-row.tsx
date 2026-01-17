import { Eye, Book, ThumbsUp, Star } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatsRowProps {
  views: number;
  episodeCount: number;
  recommendCount: number;
  rating?: number;
  className?: string;
}

function formatNumber(num: number): string {
  if (num >= 1000000) {
    const m = num / 1000000;
    return `${Number(m.toFixed(2))}M`;
  }
  if (num >= 1000) {
    const k = num / 1000;
    return `${Number(k.toFixed(1))}K`;
  }
  return num.toString();
}

export function StatsRow({
  views,
  episodeCount,
  recommendCount,
  rating,
  className,
}: StatsRowProps) {
  return (
    <div className={cn('flex items-center gap-4 text-sm text-muted-foreground', className)}>
      <div className="flex items-center gap-1" title="조회수">
        <Eye className="h-4 w-4" aria-hidden="true" />
        <span>{formatNumber(views)}</span>
      </div>
      <div className="flex items-center gap-1" title="회차수">
        <Book className="h-4 w-4" aria-hidden="true" />
        <span>{formatNumber(episodeCount)}</span>
      </div>
      <div className="flex items-center gap-1" title="추천수">
        <ThumbsUp className="h-4 w-4" aria-hidden="true" />
        <span>{formatNumber(recommendCount)}</span>
      </div>
      {rating !== undefined && (
        <div className="flex items-center gap-1 text-primary" title="평점">
          <Star className="h-4 w-4 fill-current" aria-hidden="true" />
          <span className="font-semibold">{rating}</span>
        </div>
      )}
    </div>
  );
}

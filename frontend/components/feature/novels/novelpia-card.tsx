import Image from 'next/image';
import Link from 'next/link';
import { Novel } from '@/types/novels.types';
import { NovelBadge } from './novel-badge';
import { StatsRow } from './stats-row';
import { HashtagPills } from './hashtag-pills';
import { cn } from '@/lib/utils';
import { getAgeRatingLabel, getGenreLabel } from '@/lib/utils/mappings';

interface NovelpiaCardProps {
  novel: Novel;
  className?: string;
}

function getRelativeTime(dateString: string): string {
  const now = new Date();
  const date = new Date(dateString);
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return '방금 전';

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return `${diffInMinutes}분전`;

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours}시간전`;

  const diffInDays = Math.floor(diffInHours / 24);
  return `${diffInDays}일전`;
}

export function NovelpiaCard({ novel, className }: NovelpiaCardProps) {
  const relativeTime = getRelativeTime(novel.updated_at);
  const tags = [getGenreLabel(novel.genre), getAgeRatingLabel(novel.age_rating)];

  return (
    <Link 
      href={`/novels/${novel.id}`}
      className={cn('flex gap-4 p-4 border rounded-lg bg-card text-card-foreground shadow-sm hover:border-primary/50 transition-colors', className)}
    >
      <div className="relative w-24 sm:w-32 aspect-[3/4] flex-shrink-0 overflow-hidden rounded-md border">
        <Image
          src={novel.cover_image_url || '/placeholder.png'}
          alt={novel.title}
          fill
          className="object-cover"
          sizes="(max-width: 640px) 96px, 128px"
        />
      </div>

      <div className="flex flex-col flex-1 min-w-0 py-0.5">
        <div className="flex items-start justify-between gap-2 mb-1.5">
          <div className="flex flex-wrap items-center gap-2 overflow-hidden min-h-6">
            <NovelBadge isPremium={novel.is_premium} isExclusive={novel.is_exclusive} />
            <h3 className="font-bold text-base sm:text-lg truncate" title={novel.title}>
              {novel.title}
            </h3>
          </div>
          <span className="text-sm text-muted-foreground whitespace-nowrap flex-shrink-0">
            {novel.author.nickname}
          </span>
        </div>

        <p className="text-sm text-muted-foreground line-clamp-2 mb-3 h-10">
          {novel.description}
        </p>

        <StatsRow
          views={novel.total_view_count}
          episodeCount={novel.total_chapter_count}
          recommendCount={novel.total_like_count}
          className="mb-3"
        />

        <HashtagPills tags={tags} maxDisplay={5} />

        <div className="mt-auto flex justify-end">
          <span className="text-xs text-muted-foreground font-medium">
            {relativeTime} UP
          </span>
        </div>
      </div>
    </Link>
  );
}

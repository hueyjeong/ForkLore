import Image from 'next/image';
import Link from 'next/link';
import { Novel } from '@/types/novels.types';
import { NovelBadge } from './novel-badge';
import { StatsRow } from './stats-row';
import { HashtagPills } from './hashtag-pills';
import { cn } from '@/lib/utils';

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

import { getAgeRatingLabel, getGenreLabel } from '@/lib/utils/mappings';

// ...

export function NovelpiaCard({ novel, className }: NovelpiaCardProps) {
  const relativeTime = getRelativeTime(novel.updated_at);
  const tags = [getGenreLabel(novel.genre), getAgeRatingLabel(novel.age_rating)];

  return (
    <Link 
      href={`/novels/${novel.id}`}
// ...
        <HashtagPills tags={tags} maxDisplay={5} />
// ...
          <span className="text-xs text-muted-foreground font-medium">
            {relativeTime} UP
          </span>
        </div>
      </div>
    </Link>
  );
}

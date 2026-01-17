import Image from 'next/image';
import Link from 'next/link';
import { Star, Eye } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { RankingNovel } from '@/lib/mock-data';

interface RankingListProps {
  novels: RankingNovel[];
}

function getRankBadgeClass(rank: number): string {
  if (rank === 1) return 'text-yellow-500';
  if (rank === 2) return 'text-gray-400';
  if (rank === 3) return 'text-orange-500';
  return 'text-muted-foreground';
}

export function RankingList({ novels }: RankingListProps) {
  if (novels.length === 0) {
    return (
      <div className="flex items-center justify-center py-20 text-muted-foreground">
        랭킹 데이터가 없습니다
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {novels.map((novel, index) => {
        const rank = index + 1;
        return (
          <Link
            key={novel.id}
            href={`/novels/${novel.id}`}
            className="flex items-center gap-4 rounded-xl p-3 transition-colors hover:bg-muted/50"
          >
            <div
              data-testid={`rank-badge-${rank}`}
              className={cn(
                'flex h-10 w-10 shrink-0 items-center justify-center font-serif text-xl font-bold',
                getRankBadgeClass(rank)
              )}
            >
              {rank}
            </div>

            <div className="relative h-16 w-12 shrink-0 overflow-hidden rounded-lg">
              <Image
                src={novel.coverUrl}
                alt={novel.title}
                fill
                className="object-cover"
              />
            </div>

            <div className="min-w-0 flex-1">
              <h3 className="truncate font-serif font-bold text-premium">
                {novel.title}
              </h3>
              <p className="truncate text-sm text-muted-foreground">
                {novel.author}
              </p>
            </div>

            <div className="flex shrink-0 items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Eye className="h-4 w-4" />
                <span>{novel.views}</span>
              </div>
              <div className="flex items-center gap-1 text-primary">
                <Star className="h-4 w-4 fill-current" />
                <span className="font-semibold">{novel.rating}</span>
              </div>
            </div>
          </Link>
        );
      })}
    </div>
  );
}

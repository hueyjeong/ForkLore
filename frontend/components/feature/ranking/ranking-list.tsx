import { cn } from '@/lib/utils';
import type { Novel } from '@/types/novels.types';
import { NovelpiaCard } from '@/components/feature/novels/novelpia-card';

interface RankingListProps {
  novels: Novel[];
  isLoading?: boolean;
}

function getRankBadgeClass(rank: number): string {
  if (rank === 1) return 'text-yellow-500';
  if (rank === 2) return 'text-gray-400';
  if (rank === 3) return 'text-orange-500';
  return 'text-muted-foreground';
}

export function RankingList({ novels, isLoading }: RankingListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center font-serif text-xl font-bold text-muted-foreground/20">
              {i + 1}
            </div>
            <div className="flex-1 h-32 rounded-lg bg-muted/50 animate-pulse" />
          </div>
        ))}
      </div>
    );
  }

  if (novels.length === 0) {
    return (
      <div className="flex items-center justify-center py-20 text-muted-foreground">
        랭킹 데이터가 없습니다
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {novels.map((novel, index) => {
        const rank = index + 1;
        return (
          <div key={novel.id} className="flex items-center gap-4">
            <div
              data-testid={`rank-badge-${rank}`}
              className={cn(
                'flex h-10 w-10 shrink-0 items-center justify-center font-serif text-xl font-bold',
                getRankBadgeClass(rank)
              )}
            >
              {rank}
            </div>
            <NovelpiaCard novel={novel} className="flex-1" />
          </div>
        );
      })}
    </div>
  );
}

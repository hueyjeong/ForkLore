import { cn } from '@/lib/utils';
import type { RankingNovel } from '@/lib/mock-data';
import { NovelpiaCard } from '@/components/feature/novels/novelpia-card';

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

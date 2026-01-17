import { NovelCard } from '@/components/feature/novel/novel-card';
import type { Novel } from '@/lib/mock-data';

interface NovelGridProps {
  novels: Novel[];
}

export function NovelGrid({ novels }: NovelGridProps) {
  if (novels.length === 0) {
    return (
      <div className="flex items-center justify-center py-20 text-muted-foreground">
        표시할 작품이 없습니다
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {novels.map((novel) => (
        <NovelCard
          key={novel.id}
          id={novel.id}
          title={novel.title}
          author={novel.author}
          coverUrl={novel.coverUrl}
          genre={novel.genre}
          rating={novel.rating}
        />
      ))}
    </div>
  );
}

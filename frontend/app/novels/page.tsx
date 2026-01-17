import { Suspense } from 'react';
import { NovelFilters } from '@/components/feature/novels/novel-filters';
import { NovelListWrapper } from '@/components/feature/novels/novel-list-wrapper';

export default function NovelsPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto max-w-6xl px-4 py-8">
        <h1 className="mb-8 font-serif text-3xl font-bold text-premium">
          작품
        </h1>

        <div className="space-y-6">
          <Suspense fallback={<div className="h-32 animate-pulse bg-muted rounded-lg" />}>
            <NovelFilters />
          </Suspense>

          <Suspense fallback={<div className="h-96 animate-pulse bg-muted rounded-lg" />}>
            <NovelListWrapper />
          </Suspense>
        </div>
      </main>
    </div>
  );
}

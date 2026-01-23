import { Suspense } from 'react';
import { NovelFilters } from '@/components/feature/novels/novel-filters';
import { NovelListWrapper } from '@/components/feature/novels/novel-list-wrapper';
import { CategoryTabsWrapper } from '@/components/feature/novels/category-tabs-wrapper';

export default function NovelsPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto max-w-6xl px-4 py-8 scroll-pt-16">
        <h1 className="mb-8 font-serif text-3xl font-bold text-premium">
          작품
        </h1>

        <div className="space-y-6">
          <Suspense fallback={<div className="h-10 animate-pulse bg-muted rounded" />}>
            <CategoryTabsWrapper />
          </Suspense>
          <Suspense fallback={<div className="h-12 animate-pulse bg-muted rounded" />}>
            <NovelFilters />
          </Suspense>
          <Suspense fallback={<div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"><div className="h-40 animate-pulse bg-muted rounded" /></div>}>
            <NovelListWrapper />
          </Suspense>
        </div>
      </main>
    </div>
  );
}

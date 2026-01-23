import { Suspense } from 'react';
import { RankingHeader } from '@/components/feature/ranking/ranking-header';
import { RankingTabs } from '@/components/feature/ranking/ranking-tabs';

export default function RankingPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto max-w-6xl px-4 py-8">
        <RankingHeader />
        <div className="mt-8">
          <Suspense fallback={<div className="h-40 animate-pulse bg-muted rounded" />}>
            <RankingTabs />
          </Suspense>
        </div>
      </main>
    </div>
  );
}

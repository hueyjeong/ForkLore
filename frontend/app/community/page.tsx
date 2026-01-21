import { Suspense } from 'react';
import { CategoryTabs } from '@/components/feature/community/category-tabs';
import { Skeleton } from '@/components/ui/skeleton';

// TODO: 백엔드 커뮤니티 API 구현 후 연동

export default function CommunityPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto max-w-6xl px-4 py-8">
        <div className="space-y-2 mb-8">
          <h1 className="text-3xl font-bold text-premium">커뮤니티</h1>
          <p className="text-muted-foreground">독자들과 함께 소통하세요</p>
        </div>
        <Suspense fallback={<CommunityPageLoading />}>
          <CategoryTabs />
        </Suspense>
      </main>
    </div>
  );
}

function CommunityPageLoading() {
  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Skeleton className="h-9 w-20" />
        <Skeleton className="h-9 w-20" />
      </div>
      <div className="grid grid-cols-4 gap-2">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
      </div>
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    </div>
  );
}

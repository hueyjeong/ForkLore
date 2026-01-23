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
          <CategoryTabsWrapper />
          <NovelFilters />
          <NovelListWrapper />
        </div>
      </main>
    </div>
  );
}

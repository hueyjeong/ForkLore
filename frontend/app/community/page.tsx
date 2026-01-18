import { CategoryTabs } from '@/components/feature/community/category-tabs';

export default function CommunityPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto max-w-6xl px-4 py-8">
        <div className="space-y-2 mb-8">
          <h1 className="text-3xl font-bold text-premium">커뮤니티</h1>
          <p className="text-muted-foreground">독자들과 함께 소통하세요</p>
        </div>
        <CategoryTabs />
      </main>
    </div>
  );
}

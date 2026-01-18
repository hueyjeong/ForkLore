'use client';

import { Suspense, useCallback } from 'react';
import { useSearchParams, useRouter, usePathname } from 'next/navigation';
import { Search, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { NovelFilters } from '@/components/feature/novels/novel-filters';
import { InfiniteNovelList } from '@/components/feature/novels/infinite-novel-list';

function SearchPageContent() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const currentSearch = searchParams.get('q') || '';
  const currentType = searchParams.get('type') || 'novel';
  
  // Reuse params from wrapper logic for the novel list
  const genre = searchParams.get('genre') || undefined;
  const status = searchParams.get('status') || undefined;
  const category = searchParams.get('category') || undefined;
  const sort = (searchParams.get('sort') as 'popular' | 'latest') || 'popular';

  const handleSearch = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const params = new URLSearchParams(searchParams.toString());
      if (e.target.value) {
        params.set('q', e.target.value);
      } else {
        params.delete('q');
      }
      // Use replace to avoid polluting history with every keystroke
      router.replace(`${pathname}?${params.toString()}`);
    },
    [router, pathname, searchParams]
  );

  const handleTypeChange = (value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set('type', value);
    router.push(`${pathname}?${params.toString()}`);
  };

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto max-w-6xl px-4 py-8 md:py-12">
        <div className="flex flex-col space-y-8">
          <div className="space-y-4">
            <h1 className="font-serif text-3xl md:text-4xl font-bold text-foreground">
              검색
            </h1>
            <p className="text-muted-foreground text-lg">
              원하는 작품, 브랜치, 작가를 찾아보세요.
            </p>
            
            {/* Global Search Bar */}
            <div className="relative max-w-2xl">
              <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="검색어를 입력하세요..."
                className="pl-12 h-14 text-lg shadow-sm border-2 focus-visible:ring-offset-2 transition-all"
                defaultValue={currentSearch}
                onChange={handleSearch}
              />
            </div>
          </div>

          <Tabs defaultValue={currentType} onValueChange={handleTypeChange} className="w-full">
            <TabsList className="grid w-full grid-cols-3 lg:w-[400px] mb-8">
              <TabsTrigger value="novel" className="text-base py-2">작품</TabsTrigger>
              <TabsTrigger value="branch" className="text-base py-2">브랜치</TabsTrigger>
              <TabsTrigger value="author" className="text-base py-2">작가</TabsTrigger>
            </TabsList>
            
            <TabsContent value="novel" className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
              <div className="rounded-xl border bg-card p-6 shadow-sm">
                <NovelFilters showSearch={false} />
              </div>
              <InfiniteNovelList
                genre={genre}
                status={status}
                category={category}
                sort={sort}
                searchQuery={currentSearch}
              />
            </TabsContent>
            
            <TabsContent value="branch" className="animate-in fade-in slide-in-from-bottom-2 duration-500">
              <div className="flex flex-col items-center justify-center py-20 text-center space-y-4 border-2 border-dashed rounded-xl bg-muted/30">
                <div className="p-4 rounded-full bg-muted">
                  <Search className="h-8 w-8 text-muted-foreground" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-semibold">브랜치 검색 준비 중</h3>
                  <p className="text-muted-foreground">
                    브랜치 검색 기능은 곧 제공될 예정입니다.
                  </p>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="author" className="animate-in fade-in slide-in-from-bottom-2 duration-500">
               <div className="flex flex-col items-center justify-center py-20 text-center space-y-4 border-2 border-dashed rounded-xl bg-muted/30">
                <div className="p-4 rounded-full bg-muted">
                  <Search className="h-8 w-8 text-muted-foreground" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-semibold">작가 검색 준비 중</h3>
                  <p className="text-muted-foreground">
                    작가 검색 기능은 곧 제공될 예정입니다.
                  </p>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    }>
      <SearchPageContent />
    </Suspense>
  );
}

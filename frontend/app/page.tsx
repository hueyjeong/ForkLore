import React, { Suspense } from 'react';
import { HeroSection } from '@/components/feature/home/hero-section';
import { RankingCarousel } from '@/components/feature/home/ranking-carousel';
import { RecommendationList } from '@/components/feature/home/recommendation-list';
import { GenreFilter } from '@/components/feature/home/genre-filter';

export default async function HomePage({ searchParams }: { searchParams: Promise<{ genre?: string }> }) {
  const resolvedSearchParams = await searchParams;
  const genre = resolvedSearchParams.genre;

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <HeroSection />

      {/* Main Content */}
      <main className="space-y-4 pb-20">
        
        {/* Genre Filter (Sticky) */}
        <section className="container mx-auto max-w-6xl">
          <Suspense fallback={<div className="h-[60px]" />}>
            <GenreFilter />
          </Suspense>
        </section>
        
        {/* Rankings */}
        <section className="container mx-auto max-w-6xl">
          <RankingCarousel />
        </section>

        {/* Recommendations */}
        <section className="bg-muted/30">
          <div className="container mx-auto max-w-6xl">
            <Suspense fallback={<div className="py-8 text-center text-muted-foreground">추천 작품을 불러오는 중...</div>}>
              <RecommendationList genre={genre} />
            </Suspense>
          </div>
        </section>
      </main>
    </div>
  );
}

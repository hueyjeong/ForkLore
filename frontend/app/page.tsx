import React, { Suspense } from 'react';
import { HeroSection } from '@/components/feature/home/hero-section';
import { RankingCarousel } from '@/components/feature/home/ranking-carousel';
import { RecommendationList } from '@/components/feature/home/recommendation-list';
import { GenreFilter } from '@/components/feature/home/genre-filter';

function RecommendationWrapper({ searchParams }: { searchParams: Promise<{ genre?: string }> }) {
  const params = React.use(searchParams);
  return <RecommendationList genre={params.genre} />;
}

export default async function HomePage({ searchParams }: { searchParams: Promise<{ genre?: string }> }) {
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
            <Suspense fallback={<div className="py-8">Loading...</div>}>
              <RecommendationWrapper searchParams={searchParams} />
            </Suspense>
          </div>
        </section>
      </main>
    </div>
  );
}

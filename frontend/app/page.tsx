import React from 'react';
import { HeroSection } from '@/components/feature/home/hero-section';
import { RankingCarousel } from '@/components/feature/home/ranking-carousel';
import { RecommendationList } from '@/components/feature/home/recommendation-list';
import { GenreFilter } from '@/components/feature/home/genre-filter';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <HeroSection />

      {/* Main Content */}
      <main className="space-y-4 pb-20">
        
        {/* Genre Filter (Sticky) */}
        <section className="container mx-auto max-w-6xl">
          <GenreFilter />
        </section>
        
        {/* Rankings */}
        <section className="container mx-auto max-w-6xl">
          <RankingCarousel />
        </section>

        {/* Recommendations */}
        <section className="bg-muted/30">
          <div className="container mx-auto max-w-6xl">
             <RecommendationList />
          </div>
        </section>
      </main>
    </div>
  );
}

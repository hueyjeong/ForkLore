'use client';

import { HeroSection } from '@/components/feature/home/hero-section';
import { FeaturedNovelList } from '@/components/feature/home/featured-novel-list';

export default function HomePage() {
  return (
    <div className="flex flex-col w-full pb-20">
      <HeroSection />
      <FeaturedNovelList />
      
      {/* Additional sections can be added here as the platform grows */}
      <section className="py-20 bg-muted/30">
        <div className="container px-4 md:px-8 mx-auto text-center max-w-2xl">
          <h2 className="text-3xl font-bold font-serif text-premium mb-6">나만의 전설을 써내려가세요</h2>
          <p className="text-muted-foreground mb-10 leading-relaxed">
            ForkLore는 작가와 독자가 함께 소통하며 이야기를 만들어가는 열린 멀티버스 플랫폼입니다.<br />
            지금 바로 당신의 이야기를 시작하세요.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
             <div className="p-6 rounded-2xl glass border-border/50 flex flex-col gap-2 w-full sm:w-64">
                <span className="text-3xl font-bold text-primary">1,200+</span>
                <span className="text-sm font-medium text-muted-foreground">연재 중인 작품</span>
             </div>
             <div className="p-6 rounded-2xl glass border-border/50 flex flex-col gap-2 w-full sm:w-64">
                <span className="text-3xl font-bold text-primary">45k+</span>
                <span className="text-sm font-medium text-muted-foreground">활발한 독자들</span>
             </div>
             <div className="p-6 rounded-2xl glass border-border/50 flex flex-col gap-2 w-full sm:w-64">
                <span className="text-3xl font-bold text-primary">890+</span>
                <span className="text-sm font-medium text-muted-foreground">활동 중인 작가</span>
             </div>
          </div>
        </div>
      </section>
    </div>
  );
}

'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { BookOpen, PenTool } from 'lucide-react';
import { useState, useEffect } from 'react';
import { RANKING_NOVELS } from '@/lib/mock-data';

export function HeroSection() {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentImageIndex((prev) => (prev + 1) % RANKING_NOVELS.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <section className="relative h-[80vh] min-h-[600px] w-full overflow-hidden">
      {/* Background Image Carousel */}
      <AnimatePresence mode="popLayout">
        <motion.div
          key={currentImageIndex}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1.5 }}
          className="absolute inset-0 z-0"
        >
          <div
            className="absolute inset-0 bg-cover bg-center bg-no-repeat transition-transform duration-[10000ms] ease-linear hover:scale-105"
            style={{
              backgroundImage: `url('${RANKING_NOVELS[currentImageIndex].cover}')`,
            }}
          />
        </motion.div>
      </AnimatePresence>

      {/* Overlay Gradient */}
      <div className="absolute inset-0 z-10 bg-gradient-to-b from-background/30 via-background/60 to-background" />

      {/* Content */}
      <div className="container relative z-20 flex h-full flex-col items-center justify-center text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="space-y-6 max-w-4xl"
        >
          <h1 className="text-5xl font-bold tracking-tight sm:text-7xl">
            당신의 이야기가 <span className="text-primary italic">갈라지는 곳</span>
          </h1>
          
          <p className="mx-auto max-w-2xl text-lg text-muted-foreground sm:text-xl">
            ForkLore에서 수많은 선택의 갈래를 따라 펼쳐지는 당신만의 전설을 발견하세요.
          </p>

          <div className="flex flex-col gap-4 sm:flex-row sm:justify-center pt-8">
            <Button size="lg" className="gap-2 text-lg h-14 px-8">
              <BookOpen className="h-5 w-5" />
              작품 읽기
            </Button>
            <Button size="lg" variant="outline" className="gap-2 text-lg h-14 px-8 backdrop-blur-sm bg-background/50 hover:bg-background/80">
              <PenTool className="h-5 w-5" />
              연재 시작하기
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

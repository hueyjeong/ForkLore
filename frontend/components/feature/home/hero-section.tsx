'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export function HeroSection() {
  return (
    <section className="relative h-[80vh] min-h-[600px] w-full flex items-center justify-center overflow-hidden">
      {/* Background with Gradient Overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center transition-transform duration-[10000ms] scale-110 hover:scale-100"
        style={{ backgroundImage: "url('/hero_background_abstract_multiverse.png')" }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-background/20 via-background/60 to-background" />
      
      {/* Content */}
      <div className="container relative z-10 px-4 md:px-8 text-center sm:text-left">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="max-w-3xl"
        >
          <h1 className="text-5xl md:text-7xl font-bold font-serif tracking-tight text-premium mb-6">
            당신의 이야기가<br />
            <span className="text-primary italic">갈라지는</span> 곳
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-8 leading-relaxed max-w-2xl">
            ForkLore에서 수많은 선택의 갈래를 따라 펼쳐지는<br />
            당신만의 전설을 발견하세요.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center sm:justify-start">
            <Button size="lg" asChild className="grad-primary text-white h-14 px-8 text-lg font-semibold rounded-full hover:opacity-90 transition-all shadow-lg shadow-primary/20">
              <Link href="/novels">작품 읽기</Link>
            </Button>
            <Button size="lg" variant="outline" asChild className="h-14 px-8 text-lg font-semibold rounded-full glass border-border/50 hover:bg-accent/50 transition-all">
              <Link href="/publish">연재 시작하기</Link>
            </Button>
          </div>
        </motion.div>
      </div>
      
      {/* Scroll Indicator */}
      <motion.div 
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        className="absolute bottom-10 left-1/2 -translate-x-1/2 opacity-50"
      >
        <div className="w-1 h-12 rounded-full bg-gradient-to-b from-primary to-transparent" />
      </motion.div>
    </section>
  );
}

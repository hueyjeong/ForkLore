'use client';

import { NovelCard } from '@/components/feature/novel/novel-card';
import { Button } from '@/components/ui/button';
import { ChevronRight } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';

const MOCK_NOVELS = [
  {
    id: '1',
    title: '심해의 파수꾼',
    author: '바다의 전설',
    genre: '판타지',
    coverUrl: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&q=80&w=400',
    rating: 4.8,
  },
  {
    id: '2',
    title: '은하계의 그림자',
    author: '스페이스 카우보이',
    genre: 'SF',
    coverUrl: 'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&q=80&w=400',
    rating: 4.5,
  },
  {
    id: '3',
    title: '시간의 톱니바퀴',
    author: '클락마스터',
    genre: '스팀펑크',
    coverUrl: 'https://images.unsplash.com/photo-1509021436665-8f07dbf5bf1d?auto=format&fit=crop&q=80&w=400',
    rating: 4.9,
  },
  {
    id: '4',
    title: '검은 숲의 비명',
    author: '쉐도우',
    genre: '호러',
    coverUrl: 'https://images.unsplash.com/photo-1505635330303-d3f146aa1a60?auto=format&fit=crop&q=80&w=400',
    rating: 4.2,
  },
  {
    id: '5',
    title: '황제의 선택',
    author: '노블',
    genre: '로맨스 판타지',
    coverUrl: 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&q=80&w=400',
    rating: 4.7,
  },
];

export function FeaturedNovelList() {
  return (
    <section className="py-20 md:py-32 w-full container px-4 md:px-8 mx-auto">
      <div className="flex items-end justify-between mb-12">
        <motion.div
           initial={{ opacity: 0, x: -20 }}
           whileInView={{ opacity: 1, x: 0 }}
           viewport={{ once: true }}
           transition={{ duration: 0.6 }}
        >
          <h2 className="text-3xl md:text-4xl font-bold font-serif text-premium mb-2">인기 작품</h2>
          <p className="text-muted-foreground">지금 가장 많은 관심을 받고 있는 이야기들을 만나보세요.</p>
        </motion.div>
        <Button variant="ghost" asChild className="group text-primary hover:text-primary hover:bg-transparent">
          <Link href="/novels" className="flex items-center gap-1 font-semibold">
            전체 보기
            <ChevronRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </Button>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 md:gap-8">
        {MOCK_NOVELS.map((novel, index) => (
          <motion.div
            key={novel.id}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <NovelCard {...novel} />
          </motion.div>
        ))}
      </div>
    </section>
  );
}

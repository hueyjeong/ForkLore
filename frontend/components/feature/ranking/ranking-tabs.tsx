'use client';

import { useMemo } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RankingList } from './ranking-list';
import { RANKING_NOVELS, type RankingNovel } from '@/lib/mock-data';
import { parseViews } from '@/lib/utils';

function sortByViews(novels: RankingNovel[]): RankingNovel[] {
  return [...novels].sort((a, b) => parseViews(b.views) - parseViews(a.views));
}

function sortByRating(novels: RankingNovel[]): RankingNovel[] {
  return [...novels].sort((a, b) => b.rating - a.rating);
}

export function RankingTabs() {
  const dailyRanking = useMemo(() => sortByViews(RANKING_NOVELS), []);
  const weeklyRanking = useMemo(() => sortByRating(RANKING_NOVELS), []);
  const monthlyRanking = useMemo(() => sortByViews(RANKING_NOVELS).reverse(), []);

  return (
    <Tabs defaultValue="daily" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="daily">일간</TabsTrigger>
        <TabsTrigger value="weekly">주간</TabsTrigger>
        <TabsTrigger value="monthly">월간</TabsTrigger>
      </TabsList>
      <TabsContent value="daily" className="mt-6">
        <RankingList novels={dailyRanking} />
      </TabsContent>
      <TabsContent value="weekly" className="mt-6">
        <RankingList novels={weeklyRanking} />
      </TabsContent>
      <TabsContent value="monthly" className="mt-6">
        <RankingList novels={monthlyRanking} />
      </TabsContent>
    </Tabs>
  );
}

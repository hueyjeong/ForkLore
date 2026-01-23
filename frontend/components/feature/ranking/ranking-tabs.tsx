'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useQuery } from '@tanstack/react-query';
import { getNovels } from '@/lib/api/novels.api';
import { RankingList } from './ranking-list';

export function RankingTabs() {
  const { data: dailyData, isLoading: isDailyLoading } = useQuery({
    queryKey: ['novels', 'ranking', 'daily'],
    queryFn: () => getNovels({ sort: 'total_view_count', size: 10 }),
  });

  const { data: weeklyData, isLoading: isWeeklyLoading } = useQuery({
    queryKey: ['novels', 'ranking', 'weekly'],
    queryFn: () => getNovels({ sort: 'total_like_count', size: 10 }),
  });

  const { data: monthlyData, isLoading: isMonthlyLoading } = useQuery({
    queryKey: ['novels', 'ranking', 'monthly'],
    queryFn: () => getNovels({ sort: 'total_view_count', size: 10 }),
  });

  return (
    <Tabs defaultValue="daily" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="daily">일간</TabsTrigger>
        <TabsTrigger value="weekly">주간</TabsTrigger>
        <TabsTrigger value="monthly">월간</TabsTrigger>
      </TabsList>
      <TabsContent value="daily" className="mt-6">
        <RankingList novels={dailyData?.results || []} isLoading={isDailyLoading} />
      </TabsContent>
      <TabsContent value="weekly" className="mt-6">
        <RankingList novels={weeklyData?.results || []} isLoading={isWeeklyLoading} />
      </TabsContent>
      <TabsContent value="monthly" className="mt-6">
        <RankingList novels={monthlyData?.results || []} isLoading={isMonthlyLoading} />
      </TabsContent>
    </Tabs>
  );
}


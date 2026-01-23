'use client';

import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { getPurchases } from '@/lib/api/interactions.api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, BookOpen, Calendar } from 'lucide-react';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';

export function MyLibrary() {
  const { data, isPending, isError } = useQuery({
    queryKey: ['purchases', { page: 1, size: 50 }],
    queryFn: () => getPurchases({ page: 1, size: 50 }),
  });

  const purchases = data?.results ?? [];

  useEffect(() => {
    if (isError) {
      toast.error('Failed to load library');
    }
  }, [isError]);

  if (isPending) {
    return (
      <div className="flex h-60 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">My Library</h2>
        <Badge variant="outline" className="text-lg px-4 py-1">
          {purchases.length} Items
        </Badge>
      </div>

      {purchases.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 text-muted-foreground border-2 border-dashed rounded-lg">
            <BookOpen className="w-12 h-12 mb-4 opacity-20" />
            <p>You haven't purchased any chapters yet.</p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {purchases.map((purchase, index) => (
            <motion.div
              key={purchase.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card className="hover:shadow-lg transition-shadow cursor-pointer group h-full flex flex-col justify-between">
                <CardHeader>
                    <CardTitle className="group-hover:text-primary transition-colors line-clamp-2">
                        {purchase.chapter.title}
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex justify-between items-center text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                            Chapter {purchase.chapter.chapterNumber}
                        </span>
                        <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {new Date(purchase.purchasedAt).toLocaleDateString()}
                        </span>
                    </div>
                    <div className="mt-4 flex justify-between items-center">
                        <Badge variant="secondary" className="font-mono">
                            {purchase.cost} C
                        </Badge>
                    </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

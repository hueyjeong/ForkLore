'use client';

import { useState, useMemo } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PostList } from './post-list';
import { COMMUNITY_POSTS } from '@/lib/mock-data';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

type SortMode = 'popular' | 'latest';
type Category = '전체' | '자유' | '작품토론' | '공지';

interface CategoryTabsProps {
  isLoading?: boolean;
  error?: Error | null;
  onRetry?: () => void;
}

// TODO: 백엔드 커뮤니티 API 구현 후 연동

export function CategoryTabs({ isLoading = false, error = null, onRetry }: CategoryTabsProps) {
  const [sortMode, setSortMode] = useState<SortMode>('popular');
  const [category, setCategory] = useState<Category>('전체');

  const filteredAndSortedPosts = useMemo(() => {
    if (isLoading || error) return [];

    let filtered = COMMUNITY_POSTS;

    if (category !== '전체') {
      filtered = COMMUNITY_POSTS.filter(post => post.category === category);
    }

    return [...filtered].sort((a, b) => {
      if (sortMode === 'popular') {
        return b.likeCount - a.likeCount;
      }
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    });
  }, [category, sortMode, isLoading, error]);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-4">
        <AlertCircle className="h-12 w-12 text-destructive" />
        <div className="text-center">
          <h3 className="font-semibold mb-2">게시글을 불러올 수 없습니다</h3>
          <p className="text-sm text-muted-foreground mb-4">
            잠시 후 다시 시도해주세요
          </p>
        </div>
        {onRetry && (
          <Button onClick={onRetry} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            다시 시도
          </Button>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <button
          onClick={() => setSortMode('popular')}
          className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
            sortMode === 'popular'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground hover:bg-muted/80'
          }`}
        >
          인기글
        </button>
        <button
          onClick={() => setSortMode('latest')}
          className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
            sortMode === 'latest'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground hover:bg-muted/80'
          }`}
        >
          최신글
        </button>
      </div>

      <Tabs defaultValue="전체" className="w-full" onValueChange={(v) => setCategory(v as Category)}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="전체">전체</TabsTrigger>
          <TabsTrigger value="자유">자유</TabsTrigger>
          <TabsTrigger value="작품토론">작품토론</TabsTrigger>
          <TabsTrigger value="공지">공지</TabsTrigger>
        </TabsList>
        <TabsContent value="전체" className="mt-4">
          <PostList posts={filteredAndSortedPosts} />
        </TabsContent>
        <TabsContent value="자유" className="mt-4">
          <PostList posts={filteredAndSortedPosts} />
        </TabsContent>
        <TabsContent value="작품토론" className="mt-4">
          <PostList posts={filteredAndSortedPosts} />
        </TabsContent>
        <TabsContent value="공지" className="mt-4">
          <PostList posts={filteredAndSortedPosts} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

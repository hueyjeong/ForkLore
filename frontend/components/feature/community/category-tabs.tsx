'use client';

import { useState, useMemo } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PostList } from './post-list';
import { COMMUNITY_POSTS, type CommunityPost } from '@/lib/mock-data';

type SortMode = 'popular' | 'latest';
type Category = '전체' | '자유' | '작품토론' | '공지';

export function CategoryTabs() {
  const [sortMode, setSortMode] = useState<SortMode>('popular');
  const [category, setCategory] = useState<Category>('전체');

  const filteredAndSortedPosts = useMemo(() => {
    let filtered = COMMUNITY_POSTS;
    
    // Filter by category
    if (category !== '전체') {
      filtered = COMMUNITY_POSTS.filter(post => post.category === category);
    }
    
    // Sort
    return [...filtered].sort((a, b) => {
      if (sortMode === 'popular') {
        return b.likeCount - a.likeCount;
      }
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    });
  }, [category, sortMode]);

  return (
    <div className="space-y-4">
      {/* Sort Toggle */}
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

      {/* Category Tabs */}
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

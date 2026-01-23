import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { BookOpen, Star, Share2, Heart, List, MessageCircle, ChevronLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { getNovel } from '@/lib/api/novels.api';

export default async function NovelDetailPage({ params }: { params: { id: string } }) {
  const { id } = params;

  let novel;
  try {
    novel = await getNovel(Number(id));
  } catch (error: unknown) {
    const maybeError = error as { response?: { status?: number }; status?: number };
    const status = maybeError?.response?.status ?? maybeError?.status;

    if (status === 404) {
      notFound();
    }

    console.error('Failed to fetch novel details:', error);
    throw error;
  }

  const formatViews = (views: number) => {
    if (views >= 1000000) return `${(views / 1000000).toFixed(1)}M`;
    if (views >= 1000) return `${(views / 1000).toFixed(1)}K`;
    return views.toString();
  };

  const formatLikes = (likes: number) => {
    if (likes >= 1000) return `${(likes / 1000).toFixed(1)}K`;
    return likes.toString();
  };

  const stats = {
    views: formatViews(novel.total_view_count ?? (novel as any).totalViewCount ?? 0),
    likes: formatLikes(novel.total_like_count ?? (novel as any).totalLikeCount ?? 0),
    rating: novel.average_rating ?? (novel as any).averageRating ?? 0,
  };

  const tags = [novel.genre];

  const createdAt = new Date(novel.created_at);
  const CHAPTERS = Array.from({ length: novel.total_chapter_count || 0 }).map((_, i) => {
    const chapterDate = new Date(createdAt.getTime() + i * 24 * 60 * 60 * 1000);
    return {
      id: i + 1,
      title: `Chapter ${i + 1}`,
      date: chapterDate.toISOString().split('T')[0],
      coins: i < 3 ? 0 : 10,
      isRead: false,
    };
  });
  const REVIEWS: Array<{ id: number; user: string; content: string; rating: number; date: string }> = [];

  return (
    <div className="min-h-screen bg-background pb-20 md:pb-0">
      {/* Hero Section */}
      <div className="relative h-[400px] w-full overflow-hidden md:h-[500px]">
        {/* Background Image with Blur */}
        <div className="absolute inset-0">
          <Image
            src={novel.cover_image_url}
            alt={novel.title}
            fill
            className="object-cover opacity-60 blur-sm"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-transparent" />
        </div>

        {/* Hero Content */}
        <div className="container relative z-10 mx-auto flex h-full flex-col items-center justify-end px-4 pb-8 text-center md:flex-row md:items-end md:justify-start md:text-left">
          {/* Cover Image */}
          <div className="relative mb-4 h-48 w-32 shrink-0 overflow-hidden rounded-lg shadow-2xl md:mb-0 md:mr-8 md:h-72 md:w-48">
            <Image
              src={novel.cover_image_url}
              alt={novel.title}
              fill
              className="object-cover"
            />
          </div>

          {/* Info */}
          <div className="flex flex-col items-center md:items-start">
            <Badge variant="secondary" className="mb-2 w-fit">
              {novel.status}
            </Badge>
            <h1 className="mb-2 text-3xl font-bold font-serif tracking-tight md:text-5xl lg:text-6xl text-foreground drop-shadow-md">
              {novel.title}
            </h1>
            <p className="mb-4 text-lg text-muted-foreground font-medium">
              by <span className="text-primary hover:underline cursor-pointer">{novel.author.nickname}</span>
            </p>

            {/* Stats */}
            <div className="mb-6 flex space-x-6 text-sm md:text-base">
              <div className="flex flex-col items-center md:items-start">
                <span className="font-bold text-foreground">{stats.views}</span>
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Reads</span>
              </div>
              <div className="flex flex-col items-center md:items-start">
                <span className="font-bold text-foreground">{stats.likes}</span>
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Likes</span>
              </div>
              <div className="flex flex-col items-center md:items-start">
                <span className="font-bold text-foreground">★ {stats.rating}</span>
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Rating</span>
              </div>
            </div>

            {/* Actions (Desktop) */}
            <div className="hidden gap-3 md:flex">
              <Button size="lg" className="px-8 font-semibold shadow-lg shadow-primary/20">
                <BookOpen className="mr-2 h-5 w-5" /> Read First Chapter
              </Button>
              <Button size="icon" variant="outline" className="rounded-full bg-background/50 backdrop-blur-md border-white/20 hover:bg-background/80">
                <Heart className="h-5 w-5" />
              </Button>
              <Button size="icon" variant="outline" className="rounded-full bg-background/50 backdrop-blur-md border-white/20 hover:bg-background/80">
                <Share2 className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Sticky Header (Visible on Scroll - Implementation requires scroll hook, skipped for simplicity) */}
      
      {/* Tabbed Content */}
      <div className="container mx-auto mt-8 max-w-4xl px-4">
        <Tabs defaultValue="about" className="w-full">
          <TabsList className="grid w-full grid-cols-3 rounded-xl bg-muted/50 p-1">
            <TabsTrigger value="about">About</TabsTrigger>
            <TabsTrigger value="chapters">Chapters</TabsTrigger>
            <TabsTrigger value="reviews">Reviews</TabsTrigger>
          </TabsList>

          {/* About Tab */}
          <TabsContent value="about" className="mt-6 space-y-6">
            <div className="prose prose-lg dark:prose-invert">
              <p className="whitespace-pre-line leading-relaxed text-muted-foreground">
                {novel.description}
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => (
                <Badge key={tag} variant="outline" className="px-3 py-1 text-sm">
                  #{tag}
                </Badge>
              ))}
            </div>
          </TabsContent>

          {/* Chapters Tab */}
          <TabsContent value="chapters" className="mt-6">
            <div className="rounded-xl border bg-card text-card-foreground shadow-sm">
              <ScrollArea className="h-[500px]">
                {CHAPTERS.map((chapter) => (
                  <div
                    key={chapter.id}
                    className="flex items-center justify-between border-b p-4 last:border-0 hover:bg-muted/50 transition-colors cursor-pointer group"
                  >
                    <div className="flex flex-col">
                      <span className="font-medium group-hover:text-primary transition-colors">
                        {chapter.title}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {chapter.date}
                      </span>
                    </div>
                    <div>
                      {chapter.coins === 0 ? (
                        <Badge variant="secondary" className="bg-emerald-100 text-emerald-700 hover:bg-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400">Free</Badge>
                      ) : (
                        <div className="flex items-center text-sm font-semibold text-amber-500">
                          <span className="mr-1">{chapter.coins}</span> 🪙
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </ScrollArea>
            </div>
          </TabsContent>

          {/* Reviews Tab */}
          <TabsContent value="reviews" className="mt-6">
             {REVIEWS.length > 0 ? (
               <div className="grid gap-4">
                  {REVIEWS.map((review) => (
                    <Card key={review.id} className="overflow-hidden">
                      <CardHeader className="flex flex-row items-center gap-4 space-y-0 p-4 pb-2">
                        <Avatar className="h-8 w-8">
                          <AvatarFallback>{review.user[0]}</AvatarFallback>
                        </Avatar>
                        <div className="flex flex-col">
                          <span className="text-sm font-semibold">{review.user}</span>
                          <div className="flex text-xs text-yellow-500">
                            {Array.from({ length: review.rating }).map((_, i) => (
                              <span key={i}>★</span>
                            ))}
                          </div>
                        </div>
                        <span className="ml-auto text-xs text-muted-foreground">{review.date}</span>
                      </CardHeader>
                      <CardContent className="p-4 pt-0">
                        <p className="text-sm text-muted-foreground">{review.content}</p>
                      </CardContent>
                    </Card>
                  ))}
               </div>
             ) : (
               <div className="flex flex-col items-center justify-center py-20 text-center space-y-4 border-2 border-dashed rounded-xl bg-muted/30">
                 <div className="p-4 rounded-full bg-muted">
                   <MessageCircle className="h-8 w-8 text-muted-foreground" />
                 </div>
                 <div className="space-y-2">
                   <h3 className="text-xl font-semibold">No Reviews Yet</h3>
                   <p className="text-muted-foreground">
                     Be the first to review this novel!
                   </p>
                 </div>
               </div>
             )}
          </TabsContent>
        </Tabs>
      </div>

      {/* Mobile Sticky Action Bar */}
      <div className="fixed bottom-0 left-0 right-0 border-t bg-background/80 p-4 backdrop-blur-lg md:hidden z-50">
        <Button className="w-full text-lg shadow-lg shadow-primary/20" size="lg">
          <BookOpen className="mr-2 h-5 w-5" /> Read Now
        </Button>
      </div>
    </div>
  );
}

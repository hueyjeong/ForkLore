import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { BookOpen, Star, Share2, Heart, List, MessageCircle, ChevronLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';

// Mock Data
const NOVEL = {
  id: '1',
  title: 'The Shadow of the Highborn',
  author: 'Elena Vance',
  cover: 'https://images.unsplash.com/photo-1629196914168-3a26476d90e6?q=80&w=2787&auto=format&fit=crop',
  synopsis: `In a world where magic is a currency, a young street thief discovers she possesses the ancient bloodline of the Highborn. Hunted by the empire and courted by the rebellion, she must navigate a web of intrigue, betrayal, and forbidden romance.

  As the Shadow War looms, every choice matters. Who will you trust? The charming prince with a dark secret, or the rogue assassin who saved your life?`,
  stats: {
    views: '1.2M',
    likes: '45.6K',
    rating: 4.8,
  },
  tags: ['Fantasy', 'Romance', 'Interactive', 'Royalty'],
  status: 'Ongoing',
};

const CHAPTERS = Array.from({ length: 15 }).map((_, i) => ({
  id: i + 1,
  title: `Chapter ${i + 1}: ${['The Awakening', 'Midnight Run', 'Royal Decree', 'First Encounter', 'Hidden Blade'][i % 5]}`,
  date: '2024-03-15',
  coins: i < 3 ? 0 : 15,
  isRead: i < 5,
}));

const REVIEWS = [
  { id: 1, user: 'ReaderOne', content: 'The branching path in Ch. 10 was mind-blowing!', rating: 5, date: '2h ago' },
  { id: 2, user: 'FantasyFan', content: 'Love the character development.', rating: 4, date: '5h ago' },
  { id: 3, user: 'Critic101', content: 'Pacing is a bit slow in the middle.', rating: 3, date: '1d ago' },
];

export default function NovelDetailPage({ params }: { params: { id: string } }) {
  return (
    <div className="min-h-screen bg-background pb-20 md:pb-0">
      {/* Hero Section */}
      <div className="relative h-[400px] w-full overflow-hidden md:h-[500px]">
        {/* Background Image with Blur */}
        <div className="absolute inset-0">
          <Image
            src={NOVEL.cover}
            alt={NOVEL.title}
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
              src={NOVEL.cover}
              alt={NOVEL.title}
              fill
              className="object-cover"
            />
          </div>

          {/* Info */}
          <div className="flex flex-col items-center md:items-start">
            <Badge variant="secondary" className="mb-2 w-fit">
              {NOVEL.status}
            </Badge>
            <h1 className="mb-2 text-3xl font-bold font-serif tracking-tight md:text-5xl lg:text-6xl text-foreground drop-shadow-md">
              {NOVEL.title}
            </h1>
            <p className="mb-4 text-lg text-muted-foreground font-medium">
              by <span className="text-primary hover:underline cursor-pointer">{NOVEL.author}</span>
            </p>

            {/* Stats */}
            <div className="mb-6 flex space-x-6 text-sm md:text-base">
              <div className="flex flex-col items-center md:items-start">
                <span className="font-bold text-foreground">{NOVEL.stats.views}</span>
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Reads</span>
              </div>
              <div className="flex flex-col items-center md:items-start">
                <span className="font-bold text-foreground">{NOVEL.stats.likes}</span>
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Likes</span>
              </div>
              <div className="flex flex-col items-center md:items-start">
                <span className="font-bold text-foreground">★ {NOVEL.stats.rating}</span>
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
                {NOVEL.synopsis}
              </p>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {NOVEL.tags.map((tag) => (
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

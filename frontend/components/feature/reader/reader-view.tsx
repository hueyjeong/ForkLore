'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import {
  ChevronLeft,
  ChevronRight,
  Settings,
  Menu,
  MessageSquare,
  Bookmark,
  Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { Slider } from '@/components/ui/slider';
import { getChapter } from '@/lib/api/chapters.api';
import { BranchChoices } from './branch-choices';

interface ReaderViewProps {
  chapterId: number;
  novelId: number;
}

export function ReaderView({ chapterId, novelId }: ReaderViewProps) {
  const router = useRouter();
  const { data: chapter, isPending, isError } = useQuery({
    queryKey: ['chapter', chapterId],
    queryFn: () => getChapter(Number(chapterId)),
    enabled: !!chapterId,
  });

  // Settings state
  const [fontSize, setFontSize] = useState(100);
  const [theme, setTheme] = useState<'light' | 'sepia' | 'dark'>('light');

  if (isPending) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (isError || !chapter) {
    return (
      <div className="flex h-screen w-full flex-col items-center justify-center gap-4">
        <p className="text-destructive">Failed to load chapter</p>
        <Link href={`/novels/${novelId}`}>
            <Button variant="outline">Return to Novel</Button>
        </Link>
      </div>
    );
  }

  const handleNext = () => {
    if (chapter.nextChapter?.id) {
        router.push(`/novels/${novelId}/reader/${chapter.nextChapter.id}`);
    }
  };

  const handlePrev = () => {
    if (chapter.prevChapter?.id) {
        router.push(`/novels/${novelId}/reader/${chapter.prevChapter.id}`);
    }
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
        theme === 'dark' ? 'bg-[#1a1a1a] text-gray-300' : 
        theme === 'sepia' ? 'bg-[#f4e4bc] text-gray-900' : 
        'bg-background text-foreground'
    }`}>
      {/* Header */}
      <header className="sticky top-0 z-40 flex items-center justify-between border-b bg-background/95 px-4 py-3 backdrop-blur supports-[backdrop-filter]:bg-background/60">
         <div className="flex items-center">
           <Link href={`/novels/${novelId}`}>
             <Button variant="ghost" size="icon" className="mr-2">
               <ChevronLeft className="h-5 w-5" />
             </Button>
           </Link>
           <span className="line-clamp-1 text-sm font-medium">{chapter.title}</span>
         </div>
         
         <div className="flex items-center gap-2">
             {/* Settings Sheet */}
             <Sheet>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <Settings className="h-5 w-5" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="bottom" className="h-[300px]">
                   <SheetHeader>
                     <SheetTitle>Reader Settings</SheetTitle>
                   </SheetHeader>
                   <div className="grid gap-6 py-6">
                     <div className="space-y-2">
                       <h4 className="font-medium leading-none">Font Size</h4>
                       <div className="flex items-center gap-4">
                         <span className="text-sm">A</span>
                         <Slider 
                            defaultValue={[fontSize]} 
                            max={150} 
                            min={75} 
                            step={5} 
                            onValueChange={(vals) => setFontSize(vals[0])}
                            className="flex-1" 
                         />
                         <span className="text-lg">A</span>
                       </div>
                     </div>
                     <div className="space-y-2">
                       <h4 className="font-medium leading-none">Theme</h4>
                       <div className="flex gap-2">
                         <Button variant="outline" onClick={() => setTheme('light')} className={`flex-1 bg-white text-black border-2 ${theme === 'light' ? 'border-primary' : 'border-transparent'}`}>Light</Button>
                         <Button variant="outline" onClick={() => setTheme('sepia')} className={`flex-1 bg-[#f4e4bc] text-black border-2 ${theme === 'sepia' ? 'border-primary' : 'border-transparent'}`}>Sepia</Button>
                         <Button variant="outline" onClick={() => setTheme('dark')} className={`flex-1 bg-[#1a1a1a] text-white border-2 ${theme === 'dark' ? 'border-primary' : 'border-transparent'}`}>Dark</Button>
                       </div>
                     </div>
                   </div>
                </SheetContent>
             </Sheet>
             
             {/* TOC Sheet */}
             <Sheet>
               <SheetTrigger asChild>
                 <Button variant="ghost" size="icon">
                   <Menu className="h-5 w-5" />
                 </Button>
               </SheetTrigger>
               <SheetContent side="right">
                  <SheetHeader>
                    <SheetTitle>Table of Contents</SheetTitle>
                  </SheetHeader>
                  <div className="flex items-center justify-center h-full text-muted-foreground">
                      TOC Loading...
                  </div>
               </SheetContent>
             </Sheet>
         </div>
      </header>

      {/* Content */}
      <main className="container mx-auto max-w-2xl px-6 py-8 md:py-12">
        <article 
          className="prose prose-lg dark:prose-invert prose-p:leading-relaxed prose-headings:font-serif mx-auto transition-all duration-300"
          style={{ fontSize: `${fontSize}%` }}
          dangerouslySetInnerHTML={{ __html: chapter.contentHtml }}
        />

        {/* Branch Choices */}
        <BranchChoices novelId={novelId} currentChapterNumber={chapter.chapterNumber} />
      </main>

      {/* Footer Nav */}
      <footer className="sticky bottom-0 border-t bg-background/95 p-4 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto flex max-w-2xl justify-between items-center">
           <Button 
                variant="ghost" 
                disabled={!chapter.prevChapter}
                onClick={handlePrev}
            >
             <ChevronLeft className="mr-2 h-4 w-4" /> Prev
           </Button>

           <div className="flex gap-2">
             <Button variant="ghost" size="icon"><MessageSquare className="h-4 w-4" /></Button>
             <Button variant="ghost" size="icon"><Bookmark className="h-4 w-4" /></Button>
           </div>

           <Button 
                variant="ghost" 
                disabled={!chapter.nextChapter}
                onClick={handleNext}
           >
             Next <ChevronRight className="ml-2 h-4 w-4" />
           </Button>
        </div>
      </footer>
    </div>
  );
}

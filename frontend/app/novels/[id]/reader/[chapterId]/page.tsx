import React from 'react';
import Link from 'next/link';
import { ChevronLeft, ChevronRight, Settings, Menu, MessageSquare, Share2, Bookmark } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { Slider } from '@/components/ui/slider';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

// Mock Content
const CHAPTER_CONTENT = {
  id: 1,
  title: "Chapter 1: The Awakening",
  content: `
    <p>The rain hammered against the cobblestones of the old city, a relentless rhythm that matched the pounding of Elara's heart. She pulled her cloak tighter, the soaked wool offering little protection against the biting chill of the midnight air.</p>
    
    <p>"They're coming," a voice whispered from the shadows.</p>
    
    <p>Elara spun around, her hand instinctively reaching for the dagger concealed at her waist. "Who's there?"</p>
    
    <p>A figure stepped into the dim light of the streetlamp. It was Kael, his usual cocky grin replaced by a grim line. "The Royal Guard. They know about the artifact, Elara. We have to move. Now."</p>
    
    <p>She hesitated. Leaving now meant abandoning the safehouse, leaving behind the only home she had known for the past three years. But the artifact—the Obsidian Heart—pulsed warm against her chest, a reminder of the power she now carried.</p>
    
    <p>"Where do we go?" she asked, her voice steady despite the fear coiling in her gut.</p>
    
    <p>"The Undercity," Kael replied. "It's the only place their magic can't track us."</p>
    
    <p>Elara looked back at the darkened windows of the safehouse one last time. Goodbye, she thought.</p>
    
    <p>They ran into the night, the sound of armored boots echoing in the distance behind them.</p>
    
    <hr />
    
    <p>The descent into the Undercity was treacherous. Slick ladders, crumbling stone steps, and the ever-present smell of damp earth and rust. But as they reached the lower levels, the noise of the city above faded, replaced by the hum of ancient machinery that powered the subterranean district.</p>
    
    <p>"We need to find a way to the Rebels' sanctuary," Kael said, stopping to catch his breath.</p>
    
    <p>Elara nodded. "Do you know the way?"</p>
    
    <p>"I know a guy," Kael said. "But he's not cheap."</p>
    
    <p>As they turned the corner, they were faced with a choice. To the left, a narrow alleyway that smelled of sulfur. To the right, a wider street bustling with the shadowy inhabitants of the Undercity.</p>
  `,
  prevChapter: null,
  nextChapter: 2,
  branches: [
    { id: 'b1', text: "Trust Kael's contact and head to the alley (Left)", type: 'Risk' },
    { id: 'b2', text: "Blend in with the crowd on the main street (Right)", type: 'Safe' },
  ]
};

export default function ReaderPage({ params }: { params: { id: string; chapterId: string } }) {
  // State for settings would go here (fontSize, theme, etc.) - simplified for this implementation

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
      {/* Top Bar (Immersive - disappears on scroll usually, fixed here for demo) */}
      <header className="sticky top-0 z-40 flex items-center justify-between border-b bg-background/95 px-4 py-3 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex items-center">
          <Link href={`/novels/${params.id}`}>
            <Button variant="ghost" size="icon" className="mr-2">
              <ChevronLeft className="h-5 w-5" />
            </Button>
          </Link>
          <span className="line-clamp-1 text-sm font-medium">{CHAPTER_CONTENT.title}</span>
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
                    <Slider defaultValue={[100]} max={150} min={75} step={5} className="flex-1" />
                    <span className="text-lg">A</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium leading-none">Theme</h4>
                  <div className="flex gap-2">
                    <Button variant="outline" className="flex-1 bg-white text-black border-2 border-primary">Light</Button>
                    <Button variant="outline" className="flex-1 bg-[#f4e4bc] text-black border-2 border-transparent">Sepia</Button>
                    <Button variant="outline" className="flex-1 bg-[#1a1a1a] text-white border-2 border-transparent">Dark</Button>
                  </div>
                </div>
              </div>
            </SheetContent>
          </Sheet>

          {/* Sidebar / Menu */}
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
              <ScrollArea className="h-[calc(100vh-100px)] mt-4">
                <div className="space-y-1">
                  {Array.from({ length: 15 }).map((_, i) => (
                    <Button
                      key={i}
                      variant={i + 1 === Number(params.chapterId) ? "secondary" : "ghost"}
                      className="w-full justify-start text-left"
                    >
                      Chapter {i + 1}
                    </Button>
                  ))}
                </div>
              </ScrollArea>
            </SheetContent>
          </Sheet>
        </div>
      </header>

      {/* Reader Content */}
      <main className="container mx-auto max-w-2xl px-6 py-8 md:py-12">
        <article 
          className="prose prose-lg dark:prose-invert prose-p:leading-relaxed prose-headings:font-serif mx-auto"
          dangerouslySetInnerHTML={{ __html: CHAPTER_CONTENT.content }}
        />
        
        {/* Branching Options */}
        <div className="mt-16 space-y-6">
          <div className="flex items-center gap-4">
             <Separator className="flex-1" />
             <span className="text-sm font-medium text-muted-foreground">MAKE YOUR CHOICE</span>
             <Separator className="flex-1" />
          </div>
          
          <div className="grid gap-4">
            {CHAPTER_CONTENT.branches.map((branch) => (
              <Button 
                key={branch.id} 
                variant="outline" 
                className="h-auto w-full flex-col items-start gap-1 whitespace-normal border-2 p-6 text-left hover:border-primary hover:bg-accent"
              >
                <span className="text-lg font-medium">{branch.text}</span>
                <span className={`text-xs uppercase tracking-wider ${branch.type === 'Risk' ? 'text-red-500' : 'text-emerald-500'}`}>
                  {branch.type}
                </span>
              </Button>
            ))}
          </div>
        </div>
      </main>

      {/* Bottom Bar */}
      <footer className="sticky bottom-0 border-t bg-background/95 p-4 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto flex max-w-2xl justify-between">
           <Button variant="ghost" disabled={!CHAPTER_CONTENT.prevChapter}>
             <ChevronLeft className="mr-2 h-4 w-4" /> Prev
           </Button>
           
           <div className="flex gap-2">
             <Button variant="ghost" size="icon">
               <MessageSquare className="h-4 w-4" />
             </Button>
             <Button variant="ghost" size="icon">
               <Bookmark className="h-4 w-4" />
             </Button>
           </div>

           <Button variant="ghost" disabled={!CHAPTER_CONTENT.nextChapter}>
             Next <ChevronRight className="ml-2 h-4 w-4" />
           </Button>
        </div>
      </footer>
    </div>
  );
}

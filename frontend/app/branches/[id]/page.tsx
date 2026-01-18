import React, { Suspense } from 'react';
import { getBranch } from '@/lib/api/branches.api';
import { BranchDetailHero } from '@/components/feature/novels/branch-detail-hero';
import { ChapterList } from '@/components/feature/novels/chapter-list';
import { Metadata } from 'next';

interface BranchDetailPageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: BranchDetailPageProps): Promise<Metadata> {
  const { id } = await params;
  try {
    const branch = await getBranch(parseInt(id));
    return {
      title: `${branch.name} - ForkLore`,
      description: branch.description || `Read ${branch.name} on ForkLore`,
    };
  } catch (error) {
    return {
      title: 'Branch Not Found - ForkLore',
    };
  }
}

export default async function BranchDetailPage({ params }: BranchDetailPageProps) {
  const { id } = await params;
  const branchId = parseInt(id);
  
  // Fetch branch data on the server
  const branch = await getBranch(branchId);

  return (
    <div className="min-h-screen bg-background pb-20 md:pb-0">
      <BranchDetailHero branch={branch} />
      
      <div className="container mx-auto mt-8 max-w-4xl px-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold font-serif tracking-tight">Chapters</h2>
          <span className="text-sm text-muted-foreground">{branch.chapter_count} chapters</span>
        </div>
        
        <div className="rounded-xl border bg-card/50 shadow-sm backdrop-blur-sm">
           <Suspense fallback={<div className="p-8 text-center">Loading chapters...</div>}>
            <ChapterList branchId={branchId} />
          </Suspense>
        </div>
      </div>
    </div>
  );
}

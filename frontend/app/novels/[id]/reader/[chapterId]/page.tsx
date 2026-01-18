import React from 'react';
import { ReaderView } from '@/components/feature/reader/reader-view';

interface PageProps {
  params: Promise<{
    id: string;
    chapterId: string;
  }>;
}

export default async function ReaderPage({ params }: PageProps) {
  const { id, chapterId } = await params;
  
  return (
    <ReaderView 
      novelId={parseInt(id, 10)} 
      chapterId={parseInt(chapterId, 10)} 
    />
  );
}

import { WikiList } from '@/components/feature/wiki/wiki-list';
import { Suspense } from 'react';
import { Loader2 } from 'lucide-react';

interface WikiListPageProps {
  params: Promise<{ branchId: string }>;
}

export default async function WikiListPage({ params }: WikiListPageProps) {
  const { branchId } = await params;
  const id = parseInt(branchId);

  return (
    <div className="container mx-auto px-4 py-8 md:py-12">
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">
            Wiki Database
          </h1>
          <p className="mt-2 text-muted-foreground">
            Explore characters, locations, and lore for this branch.
          </p>
        </div>
      </div>
      
      <Suspense 
        fallback={
          <div className="flex h-64 items-center justify-center">
             <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        }
      >
        <WikiList branchId={id} />
      </Suspense>
    </div>
  );
}

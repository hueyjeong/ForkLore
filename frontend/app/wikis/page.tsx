import { Suspense } from 'react';
import { WikisView } from './wikis-view';
import { BookOpen, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default async function WikisPage({
  searchParams,
}: {
  searchParams: Promise<{ branchId?: string }>;
}) {
  const { branchId } = await searchParams;

  if (!branchId) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
        <div className="text-center max-w-md space-y-4">
          <div className="mx-auto w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-4">
            <BookOpen className="w-8 h-8 text-muted-foreground" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Select a Novel Branch</h1>
          <p className="text-muted-foreground">
            To view wikis, you need to select a specific story branch first.
            Please go back to the novel page and select a branch.
          </p>
          <div className="pt-4">
            <Button asChild>
              <Link href="/novels">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Browse Novels
              </Link>
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const parsedBranchId = parseInt(branchId, 10);

  if (isNaN(parsedBranchId)) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="text-center text-destructive">
          <h1 className="text-xl font-bold">Invalid Branch ID</h1>
          <p>The provided branch ID is invalid.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto max-w-6xl px-4 py-8">
        <div className="mb-8 flex items-center justify-between">
          <h1 className="font-serif text-3xl font-bold text-premium">
            Wikis
          </h1>
        </div>

        <Suspense fallback={<div className="h-96 animate-pulse bg-muted rounded-lg" />}>
          <WikisView branchId={parsedBranchId} />
        </Suspense>
      </main>
    </div>
  );
}

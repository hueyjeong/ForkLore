import { getMap, getMaps } from '@/lib/api/maps.api';
import { MapViewer } from '@/components/feature/map/map-viewer';
import { Suspense } from 'react';

// Helper to separate data fetching from rendering to avoid try-catch in JSX flow
async function fetchMapData(branchId: number, chapterId?: number) {
  try {
    const mapsResponse = await getMaps(branchId);
    const maps = mapsResponse.results;

    if (!maps || maps.length === 0) {
      return { error: 'No maps found for this branch.', data: null };
    }

    const mapData = await getMap(maps[0].id, chapterId);
    return { error: null, data: mapData };
  } catch (error) {
    console.error('Failed to load map:', error);
    return {
      error: 'Failed to load map data. Please try again later.',
      data: null,
    };
  }
}

export default async function MapViewerPage({
  searchParams,
}: {
  searchParams: Promise<{ branchId?: string; chapterId?: string }>;
}) {
  const { branchId, chapterId } = await searchParams;

  if (!branchId) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="rounded-lg border bg-destructive/10 p-4 text-destructive">
          Branch ID is required to view maps.
        </div>
      </div>
    );
  }

  const bId = parseInt(branchId, 10);
  const cId = chapterId ? parseInt(chapterId, 10) : undefined;

  if (isNaN(bId)) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="rounded-lg border bg-destructive/10 p-4 text-destructive">
          Invalid Branch ID provided.
        </div>
      </div>
    );
  }

  const { error, data } = await fetchMapData(bId, cId);

  if (error || !data) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="rounded-lg border bg-destructive/10 p-4 text-destructive">
          {error || 'Unknown error occurred'}
        </div>
      </div>
    );
  }

  return (
    <main className="flex h-screen w-screen flex-col overflow-hidden bg-background">
      <header className="flex h-14 items-center border-b px-4">
        <h1 className="text-lg font-semibold">{data.name}</h1>
        <div className="ml-auto text-sm text-muted-foreground">
          {cId ? `Chapter Context: ${cId}` : 'Base Map'}
        </div>
      </header>
      <div className="flex-1 overflow-hidden p-4">
        <Suspense fallback={<div>Loading Map...</div>}>
          <MapViewer mapData={data} />
        </Suspense>
      </div>
    </main>
  );
}

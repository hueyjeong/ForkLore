import { WikiDetail } from '@/components/feature/wiki/wiki-detail';
import { getWiki } from '@/lib/api/wiki.api';
import { Metadata } from 'next';

interface WikiDetailPageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: WikiDetailPageProps): Promise<Metadata> {
  const { id } = await params;
  
  // Optional: Fetch for dynamic title
  // const wiki = await getWiki(parseInt(id)).catch(() => null);
  
  return {
    title: `Wiki Entry ${id} - ForkLore`,
    description: 'View character details, locations, and lore.',
  };
}

export default async function WikiDetailPage({ params }: WikiDetailPageProps) {
  const { id } = await params;
  const wikiId = parseInt(id);
  
  // Try to fetch initial data on server to hydration
  let wiki;
  try {
    wiki = await getWiki(wikiId);
  } catch (error: unknown) {
    // If server fetch fails (e.g. auth issues or 404), 
    // we'll let the client component handle the loading/error state
    // console.error("Server fetch failed:", error);
  }

  return (
    <div className="container mx-auto px-4 py-8 md:py-12">
      <WikiDetail wikiId={wikiId} initialData={wiki} />
    </div>
  );
}

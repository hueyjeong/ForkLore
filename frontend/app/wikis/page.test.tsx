import { render, screen, waitFor, fireEvent, within } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { WikisView } from './wikis-view';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import * as wikiApi from '@/lib/api/wiki.api';
import { WikiTagDefinition, WikiEntry } from '@/types/wiki.types';

// Mock the API modules
vi.mock('@/lib/api/wiki.api');

// Mock components that might cause issues
vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

// Mock framer-motion to avoid animation issues
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

const mockTags: WikiTagDefinition[] = [
  {
    id: 1,
    name: 'Character',
    color: '#FF0000',
    icon: '👤',
    description: 'Characters',
    display_order: 1,
    created_at: '2023-01-01',
  },
  {
    id: 2,
    name: 'Location',
    color: '#00FF00',
    icon: '📍',
    description: 'Locations',
    display_order: 2,
    created_at: '2023-01-01',
  },
];

const mockWikis: WikiEntry[] = [
  {
    id: 101,
    name: 'Hero',
    image_url: '',
    first_appearance: 1,
    hidden_note: '',
    ai_metadata: null,
    tags: [mockTags[0]],
    snapshots: [],
    snapshot: null,
    created_at: '2023-01-01',
    updated_at: '2023-01-01',
  },
  {
    id: 102,
    name: 'Castle',
    image_url: '',
    first_appearance: 2,
    hidden_note: '',
    ai_metadata: null,
    tags: [mockTags[1]],
    snapshots: [],
    snapshot: null,
    created_at: '2023-01-01',
    updated_at: '2023-01-01',
  },
];

describe('WikisView', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.resetAllMocks();
  });

  it('renders search input and filters', async () => {
    vi.mocked(wikiApi.getWikiTags).mockResolvedValue(mockTags);
    vi.mocked(wikiApi.getWikis).mockResolvedValue({
      results: mockWikis,
      total_count: 2,
      next: null,
      previous: null,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <WikisView branchId={1} />
      </QueryClientProvider>
    );

    // Check search input
    expect(screen.getByPlaceholderText('Search wikis...')).toBeInTheDocument();

    // Check tags (wrapped in waitFor because they load async)
    await waitFor(() => {
      // Use getAllByText because tags appear in filter AND in cards
      expect(screen.getAllByText('Character').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Location').length).toBeGreaterThan(0);
    });

    // Check wikis
    await waitFor(() => {
      expect(screen.getByText('Hero')).toBeInTheDocument();
      expect(screen.getByText('Castle')).toBeInTheDocument();
    });
  });

  it('filters by tag when clicked', async () => {
    vi.mocked(wikiApi.getWikiTags).mockResolvedValue(mockTags);
    vi.mocked(wikiApi.getWikis).mockResolvedValue({
      results: mockWikis,
      total_count: 2,
      next: null,
      previous: null,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <WikisView branchId={1} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getAllByText('Character').length).toBeGreaterThan(0);
    });

    // Click on 'Character' tag in the filter section
    const filterHeader = screen.getByText('Filter by tag');
    const filterSection = filterHeader.parentElement;
    const characterFilter = within(filterSection!).getByText('Character');
    
    fireEvent.click(characterFilter);

    // Check if getWikis was called with the tag filter
    await waitFor(() => {
        expect(wikiApi.getWikis).toHaveBeenCalledWith(1, expect.objectContaining({
            tag_id: 1
        }));
    });
  });

  it('searches when typing', async () => {
    vi.mocked(wikiApi.getWikiTags).mockResolvedValue(mockTags);
    vi.mocked(wikiApi.getWikis).mockResolvedValue({
      results: mockWikis,
      total_count: 2,
      next: null,
      previous: null,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <WikisView branchId={1} />
      </QueryClientProvider>
    );

    const input = screen.getByPlaceholderText('Search wikis...');
    fireEvent.change(input, { target: { value: 'Hero' } });

    await waitFor(() => {
      expect(wikiApi.getWikis).toHaveBeenCalledWith(1, expect.objectContaining({
          search: 'Hero'
      }));
    });
  });

  it('shows empty state when no wikis found', async () => {
    vi.mocked(wikiApi.getWikiTags).mockResolvedValue(mockTags);
    vi.mocked(wikiApi.getWikis).mockResolvedValue({
      results: [],
      total_count: 0,
      next: null,
      previous: null,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <WikisView branchId={1} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('No wiki entries found.')).toBeInTheDocument();
    });
  });
});

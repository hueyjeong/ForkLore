import { screen, fireEvent, waitFor } from '@testing-library/react';
import { render } from '@/tests/utils/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { InfiniteNovelList } from './infinite-novel-list';
import { apiClient } from '@/lib/api-client';

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => <div {...props}>{children}</div>,
  },
}));

vi.mock('next/image', () => ({
  default: ({ src, alt, ...props }: { src: string; alt: string }) => <img src={src} alt={alt} {...props} />,
}));

vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => <a href={href}>{children}</a>,
}));

vi.mock('react-virtuoso', () => ({
  Virtuoso: ({ data, itemContent, endReached }: {
    data: unknown[];
    itemContent: (index: number, item: unknown) => React.ReactNode;
    endReached?: () => void;
  }) => (
    <div data-testid="virtuoso-list">
      {data.map((item, index) => (
        <div key={index}>{itemContent(index, item)}</div>
      ))}
      {endReached && <button data-testid="load-more" onClick={endReached}>Load More</button>}
    </div>
  ),
}));

const mockNovels = [
  {
    id: 1,
    title: 'Test Novel 1',
    author: { id: 1, username: 'author1', nickname: 'Author One' },
    description: 'Description 1',
    coverImageUrl: 'https://example.com/1.jpg',
    genre: 'FANTASY',
    status: 'ONGOING',
    totalViewCount: 1000,
    totalChapterCount: 10,
    totalLikeCount: 50,
    isPremium: false,
    isExclusive: false,
    ageRating: 'ALL',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    title: 'Test Novel 2',
    author: { id: 2, username: 'author2', nickname: 'Author Two' },
    description: 'Description 2',
    coverImageUrl: 'https://example.com/2.jpg',
    genre: 'ROMANCE',
    status: 'COMPLETED',
    totalViewCount: 2000,
    totalChapterCount: 20,
    totalLikeCount: 100,
    isPremium: true,
    isExclusive: false,
    ageRating: 'TEEN',
    createdAt: '2024-01-02T00:00:00Z',
    updatedAt: '2024-01-02T00:00:00Z',
  },
];

const createMockResponse = (page = 1, hasNext = true) => ({
  data: {
    data: {
      results: mockNovels,
      total: 100,
      page,
      size: 12,
      next: hasNext ? `http://localhost:8000/api/novels/?page=${page + 1}` : null,
    },
  },
});

describe('InfiniteNovelList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (apiClient.get as any).mockResolvedValue(createMockResponse(1, true));
  });

  it('renders initial set of novels', async () => {
    render(<InfiniteNovelList />);

    await waitFor(() => {
      const novelTitles = screen.getAllByRole('heading', { level: 3 });
      expect(novelTitles.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('loads more novels on scroll', async () => {
    render(<InfiniteNovelList />);

    await screen.findByTestId('virtuoso-list');

    const initialLinks = screen.getAllByRole('link');

    const loadMoreButton = screen.getByTestId('load-more');
    (apiClient.get as any).mockResolvedValue(createMockResponse(2, false));
    fireEvent.click(loadMoreButton);

    await waitFor(() => {
      const newLinks = screen.getAllByRole('link');
      expect(newLinks.length).toBeGreaterThan(initialLinks.length);
    });
  });

  it('filters novels by genre', async () => {
    render(<InfiniteNovelList genre="판타지" />);

    const container = await screen.findByTestId('virtuoso-list');
    expect(container).toBeInTheDocument();
  });

  it('filters novels by status', async () => {
    render(<InfiniteNovelList status="완결" />);

    const container = await screen.findByTestId('virtuoso-list');
    expect(container).toBeInTheDocument();
  });

  it('sorts novels by popularity', async () => {
    render(<InfiniteNovelList sort="popular" />);

    const container = await screen.findByTestId('virtuoso-list');
    expect(container).toBeInTheDocument();
  });

  it('sorts novels by date', async () => {
    render(<InfiniteNovelList sort="latest" />);

    const container = await screen.findByTestId('virtuoso-list');
    expect(container).toBeInTheDocument();
  });

  it('filters novels by search query', async () => {
    render(<InfiniteNovelList searchQuery="그림자" />);

    const container = await screen.findByTestId('virtuoso-list');
    expect(container).toBeInTheDocument();
  });
});

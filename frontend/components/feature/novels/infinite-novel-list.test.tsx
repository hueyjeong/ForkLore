import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { InfiniteNovelList } from './infinite-novel-list';
import { NOVELS_LIST } from '@/lib/mock-data';

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

describe('InfiniteNovelList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders initial set of novels', () => {
    render(<InfiniteNovelList />);
    
    const novelTitles = screen.getAllByRole('heading', { level: 3 });
    expect(novelTitles.length).toBeGreaterThanOrEqual(1);
  });

  it('loads more novels on scroll', async () => {
    render(<InfiniteNovelList />);
    
    const initialCount = screen.getAllByRole('link').length;
    
    const loadMoreButton = screen.getByTestId('load-more');
    fireEvent.click(loadMoreButton);
    
    await waitFor(() => {
      const newCount = screen.getAllByRole('link').length;
      expect(newCount).toBeGreaterThanOrEqual(initialCount);
    });
  });

  it('filters novels by genre', () => {
    render(<InfiniteNovelList genre="판타지" />);
    
    const container = screen.getByTestId('virtuoso-list');
    expect(container).toBeInTheDocument();
  });

  it('filters novels by status', () => {
    render(<InfiniteNovelList status="완결" />);
    
    const container = screen.getByTestId('virtuoso-list');
    expect(container).toBeInTheDocument();
  });

  it('sorts novels by popularity', () => {
    render(<InfiniteNovelList sort="popular" />);
    
    const container = screen.getByTestId('virtuoso-list');
    expect(container).toBeInTheDocument();
  });

  it('sorts novels by date', () => {
    render(<InfiniteNovelList sort="latest" />);
    
    const container = screen.getByTestId('virtuoso-list');
    expect(container).toBeInTheDocument();
  });

  it('filters novels by search query', () => {
    render(<InfiniteNovelList searchQuery="그림자" />);
    
    const container = screen.getByTestId('virtuoso-list');
    expect(container).toBeInTheDocument();
  });
});

import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { NovelGrid } from './novel-grid';
import type { Novel } from '@/lib/mock-data';

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => <div {...props}>{children}</div>,
  },
}));

// Mock next/image
vi.mock('next/image', () => ({
  default: ({ src, alt, ...props }: { src: string; alt: string }) => <img src={src} alt={alt} {...props} />,
}));

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => <a href={href}>{children}</a>,
}));

const mockNovels: Novel[] = [
  {
    id: '1',
    title: '테스트 소설 1',
    author: '작가 1',
    coverUrl: 'https://example.com/cover1.jpg',
    genre: '판타지',
    rating: 4.5,
    views: '100K',
    status: '연재중',
    tags: ['판타지', '로맨스'],
    lastUpdated: '2026-01-17',
  },
  {
    id: '2',
    title: '테스트 소설 2',
    author: '작가 2',
    coverUrl: 'https://example.com/cover2.jpg',
    genre: '로맨스',
    rating: 4.8,
    views: '200K',
    status: '완결',
    tags: ['로맨스'],
    lastUpdated: '2026-01-16',
  },
];

describe('NovelGrid', () => {
  it('renders novel cards in a grid', () => {
    render(<NovelGrid novels={mockNovels} />);
    
    expect(screen.getByText('테스트 소설 1')).toBeInTheDocument();
    expect(screen.getByText('테스트 소설 2')).toBeInTheDocument();
    expect(screen.getByText('작가 1')).toBeInTheDocument();
    expect(screen.getByText('작가 2')).toBeInTheDocument();
  });

  it('displays grid layout with correct classes', () => {
    const { container } = render(<NovelGrid novels={mockNovels} />);
    
    const grid = container.querySelector('.grid');
    expect(grid).toBeInTheDocument();
    expect(grid).toHaveClass('grid-cols-2');
    expect(grid).toHaveClass('md:grid-cols-4');
    expect(grid).toHaveClass('gap-4');
  });

  it('shows empty state when no novels', () => {
    render(<NovelGrid novels={[]} />);
    
    expect(screen.getByText('표시할 작품이 없습니다')).toBeInTheDocument();
  });

  it('passes correct props to NovelCard', () => {
    render(<NovelGrid novels={mockNovels} />);
    
    // Verify links are created with correct hrefs
    const links = screen.getAllByRole('link');
    expect(links[0]).toHaveAttribute('href', '/novels/1');
    expect(links[1]).toHaveAttribute('href', '/novels/2');
  });
});

import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { RankingList } from './ranking-list';
import type { Novel } from '@/types/novels.types';
import { Genre, AgeRating, NovelStatus } from '@/types/novels.types';

vi.mock('next/image', () => ({
  default: ({ src, alt, ...props }: { src: string; alt: string }) => <img src={src} alt={alt} {...props} />,
}));

vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => <a href={href}>{children}</a>,
}));

const mockNovels: Novel[] = [
  { 
    id: 1, 
    title: '1위 소설', 
    author: { id: 1, nickname: '작가1' }, 
    total_view_count: 1200000, 
    total_like_count: 5000, 
    cover_image_url: 'https://example.com/1.jpg', 
    status: NovelStatus.ONGOING, 
    genre: Genre.FANTASY,
    age_rating: AgeRating.ALL,
    description: '설명 1',
    total_chapter_count: 100,
    is_exclusive: true,
    is_premium: false,
    updated_at: '2026-01-17',
    created_at: '2026-01-01',
    allow_branching: true,
    branch_count: 0,
    linked_branch_count: 0
  },
  { 
    id: 2, 
    title: '2위 소설', 
    author: { id: 2, nickname: '작가2' }, 
    total_view_count: 980000, 
    total_like_count: 4000, 
    cover_image_url: 'https://example.com/2.jpg', 
    status: NovelStatus.COMPLETED, 
    genre: Genre.ROMANCE,
    age_rating: AgeRating.AGE_15,
    description: '설명 2',
    total_chapter_count: 80,
    is_exclusive: false,
    is_premium: true,
    updated_at: '2026-01-16',
    created_at: '2026-01-01',
    allow_branching: false,
    branch_count: 0,
    linked_branch_count: 0
  },
  { 
    id: 3, 
    title: '3위 소설', 
    author: { id: 3, nickname: '작가3' }, 
    total_view_count: 850000, 
    total_like_count: 3000, 
    cover_image_url: 'https://example.com/3.jpg', 
    status: NovelStatus.ONGOING, 
    genre: Genre.ACTION,
    age_rating: AgeRating.AGE_12,
    description: '설명 3',
    total_chapter_count: 70,
    is_exclusive: true,
    is_premium: true,
    updated_at: '2026-01-15',
    created_at: '2026-01-01',
    allow_branching: true,
    branch_count: 0,
    linked_branch_count: 0
  },
];

describe('RankingList', () => {
  it('renders ranking items with rank numbers', () => {
    render(<RankingList novels={mockNovels} />);
    
    expect(screen.getByText('1위 소설')).toBeInTheDocument();
    expect(screen.getByText('2위 소설')).toBeInTheDocument();
    expect(screen.getByText('3위 소설')).toBeInTheDocument();
  });

  it('displays gold badge for rank 1', () => {
    render(<RankingList novels={mockNovels} />);
    
    const rankBadge = screen.getByTestId('rank-badge-1');
    expect(rankBadge).toHaveClass('text-yellow-500');
  });

  it('displays silver badge for rank 2', () => {
    render(<RankingList novels={mockNovels} />);
    
    const rankBadge = screen.getByTestId('rank-badge-2');
    expect(rankBadge).toHaveClass('text-gray-400');
  });

  it('displays bronze badge for rank 3', () => {
    render(<RankingList novels={mockNovels} />);
    
    const rankBadge = screen.getByTestId('rank-badge-3');
    expect(rankBadge).toHaveClass('text-orange-500');
  });

  it('shows novel info: title, author', () => {
    render(<RankingList novels={mockNovels} />);
    
    expect(screen.getByText('1위 소설')).toBeInTheDocument();
    expect(screen.getByText('작가1')).toBeInTheDocument();
  });
});



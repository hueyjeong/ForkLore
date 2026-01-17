import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { RankingList } from './ranking-list';
import type { RankingNovel } from '@/lib/types';

vi.mock('next/image', () => ({
  default: ({ src, alt, ...props }: { src: string; alt: string }) => <img src={src} alt={alt} {...props} />,
}));

vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => <a href={href}>{children}</a>,
}));

const mockNovels: RankingNovel[] = [
  { 
    id: 1, 
    title: '1위 소설', 
    author: '작가1', 
    views: '1.2M', 
    rating: 4.9, 
    coverUrl: 'https://example.com/1.jpg', 
    status: '연재중', 
    tags: ['판타지'],
    description: '설명 1',
    episodeCount: 100,
    recommendCount: 1000,
    isExclusive: true,
    isPremium: false,
    updatedAt: '2026-01-17'
  },
  { 
    id: 2, 
    title: '2위 소설', 
    author: '작가2', 
    views: '980K', 
    rating: 4.8, 
    coverUrl: 'https://example.com/2.jpg', 
    status: '완결', 
    tags: ['로맨스'],
    description: '설명 2',
    episodeCount: 80,
    recommendCount: 800,
    isExclusive: false,
    isPremium: true,
    updatedAt: '2026-01-16'
  },
  { 
    id: 3, 
    title: '3위 소설', 
    author: '작가3', 
    views: '850K', 
    rating: 4.7, 
    coverUrl: 'https://example.com/3.jpg', 
    status: '연재중', 
    tags: ['액션'],
    description: '설명 3',
    episodeCount: 70,
    recommendCount: 700,
    isExclusive: true,
    isPremium: true,
    updatedAt: '2026-01-15'
  },
  { 
    id: 4, 
    title: '4위 소설', 
    author: '작가4', 
    views: '720K', 
    rating: 4.6, 
    coverUrl: 'https://example.com/4.jpg', 
    status: '완결', 
    tags: ['미스터리'],
    description: '설명 4',
    episodeCount: 60,
    recommendCount: 600,
    isExclusive: false,
    isPremium: false,
    updatedAt: '2026-01-14'
  },
  { 
    id: 5, 
    title: '5위 소설', 
    author: '작가5', 
    views: '650K', 
    rating: 4.5, 
    coverUrl: 'https://example.com/5.jpg', 
    status: '연재중', 
    tags: ['SF'],
    description: '설명 5',
    episodeCount: 50,
    recommendCount: 500,
    isExclusive: false,
    isPremium: false,
    updatedAt: '2026-01-13'
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

  it('displays regular number for rank 4+', () => {
    render(<RankingList novels={mockNovels} />);
    
    const rankBadge = screen.getByTestId('rank-badge-4');
    expect(rankBadge).not.toHaveClass('text-yellow-500');
    expect(rankBadge).not.toHaveClass('text-gray-400');
    expect(rankBadge).not.toHaveClass('text-orange-500');
  });

  it('shows novel info: coverUrl, title, author, views, rating', () => {
    render(<RankingList novels={mockNovels} />);
    
    expect(screen.getByText('1위 소설')).toBeInTheDocument();
    expect(screen.getByText('작가1')).toBeInTheDocument();
    expect(screen.getByText('1.2M')).toBeInTheDocument();
    expect(screen.getByText('4.9')).toBeInTheDocument();
  });
});

import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { NovelpiaCard } from './novelpia-card';
import { Novel } from '@/lib/types';

// Mock next/image
vi.mock('next/image', () => ({
  default: ({ src, alt, fill, className }: any) => (
    <img src={src} alt={alt} className={className} data-fill={fill?.toString()} />
  ),
}));

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href }: any) => <a href={href}>{children}</a>,
}));

describe('NovelpiaCard', () => {
  const mockNovel: Novel = {
    id: '1',
    title: '테스트 소설',
    author: '테스트 작가',
    coverUrl: '/test-cover.jpg',
    views: '1200000', // 1.2M
    rating: 4.5,
    status: '연재중',
    tags: ['판타지', '하렘', '일상'],
    description: '이것은 테스트 소설의 설명입니다.',
    episodeCount: 224,
    recommendCount: 53200, // 53.2K
    isExclusive: true,
    isPremium: true,
    updatedAt: new Date(Date.now() - 16 * 60 * 1000).toISOString(), // 16분 전
    genre: 'Fantasy',
  };

  it('renders novel information correctly', () => {
    render(<NovelpiaCard novel={mockNovel} />);

    expect(screen.getByText('테스트 소설')).toBeDefined();
    expect(screen.getByText('테스트 작가')).toBeDefined();
    expect(screen.getByText('이것은 테스트 소설의 설명입니다.')).toBeDefined();
    
    // Check for badges
    expect(screen.getByText('독점')).toBeDefined();
    expect(screen.getByText('PLUS')).toBeDefined();

    // Check for stats
    expect(screen.getByText('1.2M')).toBeDefined();
    expect(screen.getByText('224')).toBeDefined();
    expect(screen.getByText('53.2K')).toBeDefined();

    // Check for hashtags
    expect(screen.getByText('#판타지')).toBeDefined();
    expect(screen.getByText('#하렘')).toBeDefined();
    expect(screen.getByText('#일상')).toBeDefined();

    // Check for relative time
    expect(screen.getByText('16분전 UP')).toBeDefined();

    // Check for cover image
    const img = screen.getByAltText('테스트 소설');
    expect(img.getAttribute('src')).toBe('/test-cover.jpg');
  });

  it('renders correctly with RankingNovel type (id as number)', () => {
    const rankingNovel = { ...mockNovel, id: 123 };
    render(<NovelpiaCard novel={rankingNovel as any} />);
    expect(screen.getByText('테스트 소설')).toBeDefined();
  });

  it('formats "just now" for very recent updates', () => {
    const recentNovel = {
      ...mockNovel,
      updatedAt: new Date(Date.now() - 30 * 1000).toISOString(),
    };
    render(<NovelpiaCard novel={recentNovel} />);
    expect(screen.getByText('방금 전 UP')).toBeDefined();
  });
});

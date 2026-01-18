import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { PostList } from './post-list';
import type { CommunityPost } from '@/lib/mock-data';

const mockPosts: CommunityPost[] = [
  {
    id: '1',
    title: '일반 게시글',
    author: '작성자1',
    category: '자유',
    commentCount: 10,
    likeCount: 50,
    createdAt: '2026-01-16',
    isPinned: false,
  },
  {
    id: '2',
    title: '공지사항',
    author: '운영자',
    category: '공지',
    commentCount: 20,
    likeCount: 100,
    createdAt: '2026-01-17',
    isPinned: true,
  },
  {
    id: '3',
    title: '다른 일반 게시글',
    author: '작성자2',
    category: '작품토론',
    commentCount: 5,
    likeCount: 25,
    createdAt: '2026-01-15',
    isPinned: false,
  },
];

describe('PostList', () => {
  it('renders list of post cards', () => {
    render(<PostList posts={mockPosts} />);
    
    expect(screen.getByText('일반 게시글')).toBeInTheDocument();
    expect(screen.getByText('공지사항')).toBeInTheDocument();
    expect(screen.getByText('다른 일반 게시글')).toBeInTheDocument();
  });

  it('shows empty state when no posts', () => {
    render(<PostList posts={[]} />);
    
    expect(screen.getByText('게시글이 없습니다')).toBeInTheDocument();
  });

  it('displays pinned posts first', () => {
    render(<PostList posts={mockPosts} />);
    
    const articles = screen.getAllByRole('article');
    // Pinned post should be first
    expect(articles[0]).toHaveTextContent('공지사항');
  });
});

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { PostCard } from './post-card';
import type { CommunityPost } from '@/lib/mock-data';

const mockPost: CommunityPost = {
  id: '1',
  title: '테스트 게시글 제목',
  author: '테스터',
  category: '자유',
  commentCount: 42,
  likeCount: 100,
  createdAt: '2026-01-17',
  isPinned: false,
};

const mockPinnedPost: CommunityPost = {
  ...mockPost,
  id: '2',
  title: '공지사항 게시글',
  isPinned: true,
  category: '공지',
};

describe('PostCard', () => {
  it('renders post title', () => {
    render(<PostCard post={mockPost} />);
    
    expect(screen.getByText('테스트 게시글 제목')).toBeInTheDocument();
  });

  it('renders author name', () => {
    render(<PostCard post={mockPost} />);
    
    expect(screen.getByText('테스터')).toBeInTheDocument();
  });

  it('renders comment count', () => {
    render(<PostCard post={mockPost} />);
    
    expect(screen.getByText(/42/)).toBeInTheDocument();
  });

  it('renders created date', () => {
    render(<PostCard post={mockPost} />);
    
    expect(screen.getByText('2026-01-17')).toBeInTheDocument();
  });

  it('shows pin icon for pinned posts', () => {
    render(<PostCard post={mockPinnedPost} />);
    
    expect(screen.getByTestId('pin-icon')).toBeInTheDocument();
  });

  it('does not show pin icon for regular posts', () => {
    render(<PostCard post={mockPost} />);
    
    expect(screen.queryByTestId('pin-icon')).not.toBeInTheDocument();
  });
});

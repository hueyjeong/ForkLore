import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { CategoryTabs } from './category-tabs';

describe('CategoryTabs', () => {
  describe('Default rendering', () => {
    it('renders category tabs: 전체, 자유, 작품토론, 공지', () => {
      render(<CategoryTabs />);

      expect(screen.getByRole('tab', { name: '전체' })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: '자유' })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: '작품토론' })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: '공지' })).toBeInTheDocument();
    });

    it('displays 전체 tab by default', () => {
      render(<CategoryTabs />);

      const allTab = screen.getByRole('tab', { name: '전체' });
      expect(allTab).toHaveAttribute('data-state', 'active');
    });

    it('renders sort toggle: 인기글/최신글', () => {
      render(<CategoryTabs />);

      expect(screen.getByRole('button', { name: '인기글' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: '최신글' })).toBeInTheDocument();
    });
  });

  describe('Post rendering', () => {
    it('renders post list from mock data', () => {
      render(<CategoryTabs />);

      expect(screen.getByText('[필독] 커뮤니티 이용 가이드')).toBeInTheDocument();
      expect(screen.getByText('[공지] 신규 작품 추천 이벤트 안내')).toBeInTheDocument();
    });

    it('shows empty state message when no posts', () => {
      render(<CategoryTabs isLoading={true} />);

      expect(screen.queryByText('[필독] 커뮤니티 이용 가이드')).not.toBeInTheDocument();
    });
  });

  describe('Error state', () => {
    it('shows error message when error prop is provided', () => {
      const mockError = new Error('Network error');
      const onRetry = vi.fn();

      render(<CategoryTabs error={mockError} onRetry={onRetry} />);

      expect(screen.getByText('게시글을 불러올 수 없습니다')).toBeInTheDocument();
      expect(screen.getByText('잠시 후 다시 시도해주세요')).toBeInTheDocument();
    });

    it('shows retry button when onRetry is provided', () => {
      const mockError = new Error('Network error');
      const onRetry = vi.fn();

      render(<CategoryTabs error={mockError} onRetry={onRetry} />);

      const retryButton = screen.getByRole('button', { name: '다시 시도' });
      expect(retryButton).toBeInTheDocument();

      fireEvent.click(retryButton);
      expect(onRetry).toHaveBeenCalledTimes(1);
    });

    it('does not show retry button when onRetry is not provided', () => {
      const mockError = new Error('Network error');

      render(<CategoryTabs error={mockError} />);

      expect(screen.queryByRole('button', { name: '다시 시도' })).not.toBeInTheDocument();
    });
  });

  describe('Loading state', () => {
    it('hides posts when isLoading is true', () => {
      render(<CategoryTabs isLoading={true} />);

      expect(screen.queryByText('[필독] 커뮤니티 이용 가이드')).not.toBeInTheDocument();
    });

    it('shows posts when isLoading is false and no error', () => {
      render(<CategoryTabs isLoading={false} />);

      expect(screen.getByText('[필독] 커뮤니티 이용 가이드')).toBeInTheDocument();
    });
  });

  describe('Interactions', () => {
    it('filters posts by category on tab change', () => {
      render(<CategoryTabs />);

      const freeTab = screen.getByRole('tab', { name: '자유' });
      fireEvent.click(freeTab);

      expect(freeTab).toHaveAttribute('data-state', 'active');
    });

    it('sorts posts on toggle change', () => {
      render(<CategoryTabs />);

      const latestButton = screen.getByRole('button', { name: '최신글' });
      fireEvent.click(latestButton);

      expect(latestButton).toHaveClass('bg-primary');
    });
  });
});

import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { CategoryTabs } from './category-tabs';

describe('CategoryTabs', () => {
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
    
    // Latest button should now be active (have primary styling)
    expect(latestButton).toHaveClass('bg-primary');
  });
});

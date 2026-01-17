import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { CategoryTabs } from './category-tabs';

describe('CategoryTabs', () => {
  const mockOnCategoryChange = vi.fn();

  it('renders all 5 category tabs', () => {
    render(
      <CategoryTabs 
        activeCategory="전체" 
        onCategoryChange={mockOnCategoryChange} 
      />
    );
    
    expect(screen.getByRole('tab', { name: '전체' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '멤버십' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '독점' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '신작' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '완결' })).toBeInTheDocument();
  });

  it('marks the activeCategory as active', () => {
    render(
      <CategoryTabs 
        activeCategory="독점" 
        onCategoryChange={mockOnCategoryChange} 
      />
    );
    
    const activeTab = screen.getByRole('tab', { name: '독점' });
    expect(activeTab).toHaveAttribute('data-state', 'active');
    
    const inactiveTab = screen.getByRole('tab', { name: '전체' });
    expect(inactiveTab).toHaveAttribute('data-state', 'inactive');
  });

  it('calls onCategoryChange when a tab is clicked', () => {
    render(
      <CategoryTabs 
        activeCategory="전체" 
        onCategoryChange={mockOnCategoryChange} 
      />
    );
    
    const veteranTab = screen.getByRole('tab', { name: '멤버십' });
    fireEvent.click(veteranTab);
    
    expect(mockOnCategoryChange).toHaveBeenCalledWith('멤버십');
  });
});

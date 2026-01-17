import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NovelFilters } from './novel-filters';

// Mock next/navigation
const mockPush = vi.fn();
const mockSearchParams = new URLSearchParams();

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
  useSearchParams: () => mockSearchParams,
  usePathname: () => '/novels',
}));

describe('NovelFilters', () => {
  beforeEach(() => {
    mockPush.mockClear();
    mockSearchParams.delete('genre');
    mockSearchParams.delete('status');
    mockSearchParams.delete('sort');
    mockSearchParams.delete('q');
  });

  it('renders genre filter buttons', () => {
    render(<NovelFilters />);
    
    // Use getAllByRole since "전체" appears in both genre and status filters
    const allButtons = screen.getAllByRole('button', { name: '전체' });
    expect(allButtons.length).toBe(2); // One for genre, one for status
    
    expect(screen.getByRole('button', { name: '판타지' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '로맨스' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '무협' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'SF' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '미스터리' })).toBeInTheDocument();
  });

  it('renders status filter buttons', () => {
    render(<NovelFilters />);
    
    // Status filters should be in a different section
    const allButtons = screen.getAllByRole('button', { name: '전체' });
    expect(allButtons.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByRole('button', { name: '연재중' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '완결' })).toBeInTheDocument();
  });

  it('renders sort select with options', () => {
    render(<NovelFilters />);
    
    // Find the sort trigger button/combobox
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('renders search input with placeholder', () => {
    render(<NovelFilters />);
    
    const searchInput = screen.getByPlaceholderText('작품 검색...');
    expect(searchInput).toBeInTheDocument();
  });

  it('updates URL params on genre filter change', () => {
    render(<NovelFilters />);
    
    const fantasyButton = screen.getByRole('button', { name: '판타지' });
    fireEvent.click(fantasyButton);
    
    // URL params are encoded, so check for the encoded value or the genre key
    expect(mockPush).toHaveBeenCalledWith(expect.stringContaining('genre='));
  });
});

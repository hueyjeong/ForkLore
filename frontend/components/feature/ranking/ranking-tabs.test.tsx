import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { RankingTabs } from './ranking-tabs';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { getNovels } from '@/lib/api/novels.api';

vi.mock('next/image', () => ({
  default: ({ src, alt, ...props }: { src: string; alt: string }) => <img src={src} alt={alt} {...props} />,
}));

vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => <a href={href}>{children}</a>,
}));

vi.mock('@/lib/api/novels.api', () => ({
  getNovels: vi.fn(),
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const Wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

describe('RankingTabs', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (getNovels as any).mockResolvedValue({ results: [] });
  });

  it('renders three tabs: 일간, 주간, 월간', () => {
    render(<RankingTabs />, { wrapper: Wrapper });
    
    expect(screen.getByRole('tab', { name: '일간' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '주간' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '월간' })).toBeInTheDocument();
  });

  it('displays 일간 tab content by default and calls API', async () => {
    render(<RankingTabs />, { wrapper: Wrapper });
    
    const dailyTab = screen.getByRole('tab', { name: '일간' });
    expect(dailyTab).toHaveAttribute('data-state', 'active');

    await waitFor(() => {
      expect(getNovels).toHaveBeenCalledWith(expect.objectContaining({ sort: 'total_view_count' }));
    });
  });

  it('switches to 주간 tab on click', async () => {
    render(<RankingTabs />, { wrapper: Wrapper });
    
    const weeklyTab = screen.getByRole('tab', { name: '주간' });
    fireEvent.click(weeklyTab);
    
    expect(weeklyTab).toHaveAttribute('data-state', 'active');
  });

  it('switches to 월간 tab on click', async () => {
    render(<RankingTabs />, { wrapper: Wrapper });
    
    const monthlyTab = screen.getByRole('tab', { name: '월간' });
    fireEvent.click(monthlyTab);
    
    expect(monthlyTab).toHaveAttribute('data-state', 'active');
  });
});


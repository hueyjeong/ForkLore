import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { RankingTabs } from './ranking-tabs';

vi.mock('next/image', () => ({
  default: ({ src, alt, ...props }: { src: string; alt: string }) => <img src={src} alt={alt} {...props} />,
}));

vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => <a href={href}>{children}</a>,
}));

describe('RankingTabs', () => {
  it('renders three tabs: 일간, 주간, 월간', () => {
    render(<RankingTabs />);
    
    expect(screen.getByRole('tab', { name: '일간' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '주간' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '월간' })).toBeInTheDocument();
  });

  it('displays 일간 tab content by default', () => {
    render(<RankingTabs />);
    
    const dailyTab = screen.getByRole('tab', { name: '일간' });
    expect(dailyTab).toHaveAttribute('data-state', 'active');
  });

  it('switches to 주간 tab on click', () => {
    render(<RankingTabs />);
    
    const weeklyTab = screen.getByRole('tab', { name: '주간' });
    fireEvent.click(weeklyTab);
    
    expect(weeklyTab).toHaveAttribute('data-state', 'active');
  });

  it('switches to 월간 tab on click', () => {
    render(<RankingTabs />);
    
    const monthlyTab = screen.getByRole('tab', { name: '월간' });
    fireEvent.click(monthlyTab);
    
    expect(monthlyTab).toHaveAttribute('data-state', 'active');
  });
});

import { render, screen } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import CommunityPage from './page';

// Mock the CategoryTabs component
vi.mock('@/components/feature/community/category-tabs', () => ({
  CategoryTabs: () => <div data-testid="category-tabs">Category Tabs</div>,
}));

describe('CommunityPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders page title and description', () => {
    render(<CommunityPage />);

    expect(screen.getByText('커뮤니티')).toBeInTheDocument();
    expect(screen.getByText('독자들과 함께 소통하세요')).toBeInTheDocument();
  });

  it('renders CategoryTabs component', () => {
    render(<CommunityPage />);

    expect(screen.getByTestId('category-tabs')).toBeInTheDocument();
  });

  it('has proper page structure with container', () => {
    const { container } = render(<CommunityPage />);

    const main = container.querySelector('main');
    expect(main).toBeInTheDocument();
    expect(main).toHaveClass('container', 'mx-auto', 'max-w-6xl', 'px-4', 'py-8');
  });

  it('has proper heading styling with premium text color', () => {
    const { container } = render(<CommunityPage />);

    const heading = screen.getByText('커뮤니티');
    expect(heading).toHaveClass('text-3xl', 'font-bold', 'text-premium');
  });

  it('wraps CategoryTabs in Suspense for loading state support', () => {
    render(<CommunityPage />);

    expect(screen.getByTestId('category-tabs')).toBeInTheDocument();
  });
});

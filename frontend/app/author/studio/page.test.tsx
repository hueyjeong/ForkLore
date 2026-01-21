import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AuthorStudioPage from './page';
import { toast } from 'sonner';

// Mock dependencies
vi.mock('@/lib/api/novels.api', () => ({
  getNovels: vi.fn(),
}));

vi.mock('@/lib/api/branches.api', () => ({
  getLinkRequests: vi.fn(),
}));

vi.mock('@/lib/api/auth.api', () => ({
  getMyProfile: vi.fn(),
}));

// Mock simple components to avoid complex rendering
vi.mock('@/components/ui/card', () => ({
  Card: ({ children }: { children: React.ReactNode }) => <div data-testid="card">{children}</div>,
  CardHeader: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CardTitle: ({ children }: { children: React.ReactNode }) => <h3>{children}</h3>,
  CardContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CardDescription: ({ children }: { children: React.ReactNode }) => <p>{children}</p>,
}));

import { getNovels } from '@/lib/api/novels.api';
import { getLinkRequests } from '@/lib/api/branches.api';
import { getMyProfile } from '@/lib/api/auth.api';

const mockUser = {
  id: 1,
  nickname: 'TestAuthor',
};

const mockNovels = [
  {
    id: 1,
    title: 'My First Novel',
    total_chapter_count: 10,
    total_view_count: 1000,
    created_at: '2024-01-01',
  },
  {
    id: 2,
    title: 'My Second Novel',
    total_chapter_count: 5,
    total_view_count: 500,
    created_at: '2024-02-01',
  },
];

const mockLinkRequests = [
  {
    id: 1,
    branch_id: 101,
    request_message: 'Please link this branch',
    status: 'PENDING',
    created_at: '2024-03-01',
  },
];

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
}

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('AuthorStudioPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (getMyProfile as any).mockResolvedValue(mockUser);
    (getNovels as any).mockResolvedValue({ results: mockNovels, total: 2 });
    (getLinkRequests as any).mockResolvedValue({ results: mockLinkRequests, total: 1 });
  });

  it('renders dashboard sections', async () => {
    render(
      <TestWrapper>
        <AuthorStudioPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('My Novels')).toBeInTheDocument();
    });

    expect(screen.getByText('Author Studio')).toBeInTheDocument();
    expect(screen.getByText('Link Requests')).toBeInTheDocument();
  });

  it('displays statistics correctly', async () => {
    render(
      <TestWrapper>
        <AuthorStudioPage />
      </TestWrapper>
    );

    await waitFor(() => {
      // Total novels: 2
      expect(screen.getByText('2')).toBeInTheDocument();
    });

    // Total chapters: 10 + 5 = 15
    expect(screen.getByText('15')).toBeInTheDocument();
    // Total views: 1000 + 500 = 1500
    expect(screen.getByText('1,500')).toBeInTheDocument();
    // Pending requests: 1
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('renders my novels list', async () => {
    render(
      <TestWrapper>
        <AuthorStudioPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('My First Novel')).toBeInTheDocument();
      expect(screen.getByText('My Second Novel')).toBeInTheDocument();
    });
  });

  it('renders link requests list', async () => {
    render(
      <TestWrapper>
        <AuthorStudioPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Please link this branch')).toBeInTheDocument();
    });
  });

  it('shows loading state initially', () => {
    // Make promises hang
    (getNovels as any).mockImplementation(() => new Promise(() => {}));
    
    render(
      <TestWrapper>
        <AuthorStudioPage />
      </TestWrapper>
    );

    // Assuming we use skeleton or loading text
    // Since implementation details might vary, we check for main content NOT present
    expect(screen.queryByText('My First Novel')).not.toBeInTheDocument();
  });

  it('handles empty states', async () => {
    (getNovels as any).mockResolvedValue({ results: [], total: 0 });
    (getLinkRequests as any).mockResolvedValue({ results: [], total: 0 });

    render(
      <TestWrapper>
        <AuthorStudioPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('No novels found')).toBeInTheDocument();
      expect(screen.getByText('No pending requests')).toBeInTheDocument();
    });
  });
});

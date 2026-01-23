import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BranchChoices } from './branch-choices';
import { toast } from 'sonner';

// Mock API client
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: {
    info: vi.fn(),
  },
}));

import { apiClient } from '@/lib/api-client';

// Mock data fixtures
const mockBranches = [
  {
    id: 1,
    novel_id: 1,
    name: 'Main Branch',
    description: 'The main storyline',
    cover_image_url: 'https://example.com/1.jpg',
    is_main: true,
    branch_type: 'MAIN',
    visibility: 'PUBLIC',
    canon_status: 'NON_CANON',
    parent_branch_id: null,
    fork_point_chapter: 3,
    vote_count: 10,
    vote_threshold: 5,
    view_count: 100,
    chapter_count: 20,
    author: { id: 1, username: 'author1', nickname: 'Author One' },
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    novel_id: 1,
    name: 'Side Story Branch',
    description: 'A side story path',
    cover_image_url: 'https://example.com/2.jpg',
    is_main: false,
    branch_type: 'SIDE_STORY',
    visibility: 'PUBLIC',
    canon_status: 'NON_CANON',
    parent_branch_id: 1,
    fork_point_chapter: 3,
    vote_count: 5,
    vote_threshold: 5,
    view_count: 50,
    chapter_count: 10,
    author: { id: 1, username: 'author1', nickname: 'Author One' },
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 3,
    novel_id: 1,
    name: 'Fan Fiction Branch',
    description: 'Fan fiction path from chapter 5',
    cover_image_url: 'https://example.com/3.jpg',
    is_main: false,
    branch_type: 'FAN_FIC',
    visibility: 'PUBLIC',
    canon_status: 'NON_CANON',
    parent_branch_id: 1,
    fork_point_chapter: 5,
    vote_count: 8,
    vote_threshold: 5,
    view_count: 80,
    chapter_count: 15,
    author: { id: 2, username: 'author2', nickname: 'Author Two' },
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

const createMockResponse = (branches: typeof mockBranches) => ({
  data: {
    data: {
      results: branches,
      total: branches.length,
      page: 1,
      size: 100,
      hasNext: false,
    },
  },
});

// Test wrapper
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: Infinity,
        staleTime: Infinity,
      },
    },
  });
}

function TestWrapper({ children }: { children: React.ReactNode }) {
  const queryClient = createTestQueryClient();
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

describe('BranchChoices', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (apiClient.get as any).mockResolvedValue(createMockResponse(mockBranches));
  });

  it('should return null during loading', async () => {
    (apiClient.get as any).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(createMockResponse(mockBranches)), 100))
    );

    const { container } = render(
      <TestWrapper>
        <BranchChoices novelId={1} currentChapterNumber={3} />
      </TestWrapper>
    );

    // Component should return null (no rendered content) during loading
    expect(container.firstChild).toBeNull();

    // Wait for loading to complete
    await waitFor(() => {
      expect(apiClient.get).toHaveBeenCalled();
    });
  });

  it('should return null when no branches match the fork point', async () => {
    const { container } = render(
      <TestWrapper>
        <BranchChoices novelId={1} currentChapterNumber={10} />
      </TestWrapper>
    );

    // Wait for query to complete
    await waitFor(() => {
      expect(apiClient.get).toHaveBeenCalledWith('/novels/1/branches', { params: { size: 100 } });
    });

    // Component should return null (no rendered content) when no matching branches
    expect(container.firstChild).toBeNull();
  });

  it('should filter branches by fork_point_chapter using select option', async () => {
    render(
      <TestWrapper>
        <BranchChoices novelId={1} currentChapterNumber={3} />
      </TestWrapper>
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Main Branch')).toBeInTheDocument();
    });

    // Should only show branches with fork_point_chapter === 3
    expect(screen.getByText('Main Branch')).toBeInTheDocument();
    expect(screen.getByText('Side Story Branch')).toBeInTheDocument();
    expect(screen.queryByText('Fan Fiction Branch')).not.toBeInTheDocument();

    // Verify the query was called with correct parameters
    expect(apiClient.get).toHaveBeenCalledWith('/novels/1/branches', { params: { size: 100 } });
  });

  it('should render branch cards with correct information', async () => {
    render(
      <TestWrapper>
        <BranchChoices novelId={1} currentChapterNumber={3} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Main Branch')).toBeInTheDocument();
    });

    // Check branch details
    expect(screen.getByText('Main Branch')).toBeInTheDocument();
    expect(screen.getByText('The main storyline')).toBeInTheDocument();
    expect(screen.getByText('MAIN')).toBeInTheDocument();
    expect(screen.getByText('20 Chapters')).toBeInTheDocument();

    expect(screen.getByText('Side Story Branch')).toBeInTheDocument();
    expect(screen.getByText('A side story path')).toBeInTheDocument();
    expect(screen.getByText('SIDE_STORY')).toBeInTheDocument();
    expect(screen.getByText('10 Chapters')).toBeInTheDocument();
  });

  it('should display toast info when branch is clicked', async () => {
    render(
      <TestWrapper>
        <BranchChoices novelId={1} currentChapterNumber={3} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Main Branch')).toBeInTheDocument();
    });

    // Click on first branch button
    const branchButton = screen.getByText('Main Branch').closest('button');
    branchButton?.click();

    // Verify toast was called
    expect(toast.info).toHaveBeenCalledWith('Selected branch: Main Branch', {
      description: 'Branch navigation to be implemented',
    });
  });

  it('should show AVAILABLE BRANCHES section separator', async () => {
    render(
      <TestWrapper>
        <BranchChoices novelId={1} currentChapterNumber={3} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('AVAILABLE BRANCHES')).toBeInTheDocument();
    });

    // Check that the separator section is visible
    expect(screen.getByText('AVAILABLE BRANCHES')).toBeInTheDocument();
  });

  it('should render in grid layout with 2 columns on medium screens', async () => {
    const { container } = render(
      <TestWrapper>
        <BranchChoices novelId={1} currentChapterNumber={3} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Main Branch')).toBeInTheDocument();
    });

    // The component uses grid with md:grid-cols-2
    const grid = container.querySelector('.grid');
    expect(grid).toBeInTheDocument();
    expect(grid).toHaveClass('md:grid-cols-2');
  });
});

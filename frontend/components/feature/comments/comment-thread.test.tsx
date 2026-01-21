import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CommentThread } from './comment-thread';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as interactionsApi from '@/lib/api/interactions.api';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/auth-store';

// Mock the API
vi.mock('@/lib/api/interactions.api', () => ({
  getComments: vi.fn(),
  createComment: vi.fn(),
  deleteComment: vi.fn(),
}));

// Mock the Auth Store
vi.mock('@/stores/auth-store', () => ({
  useAuthStore: vi.fn(),
}));

// Mock UI components
vi.mock('@/components/ui/textarea', () => ({
  Textarea: (props: any) => <textarea {...props} />,
}));

// Mock scrollIntoView
window.HTMLElement.prototype.scrollIntoView = vi.fn();

const mockUser = {
  id: 1,
  nickname: 'Test User',
  profile_image: null,
};

const mockComments = [
  {
    id: 1,
    user: { id: 2, nickname: 'Other User', profile_image: null },
    content: 'This is a comment',
    is_spoiler: false,
    is_pinned: false,
    like_count: 5,
    created_at: '2024-01-01T12:00:00Z',
    updated_at: '2024-01-01T12:00:00Z',
    reply_count: 0,
    paragraph_index: null,
    selection_start: null,
    selection_end: null,
    quoted_text: '',
    parent_id: null,
  },
  {
    id: 2,
    user: { id: 1, nickname: 'Test User', profile_image: null }, // Own comment
    content: 'My comment',
    is_spoiler: true,
    is_pinned: false,
    like_count: 0,
    created_at: '2024-01-02T12:00:00Z',
    updated_at: '2024-01-02T12:00:00Z',
    reply_count: 0,
    paragraph_index: null,
    selection_start: null,
    selection_end: null,
    quoted_text: '',
    parent_id: null,
  },
  {
    id: 3,
    user: { id: 3, nickname: 'Admin', profile_image: null },
    content: 'Pinned comment',
    is_spoiler: false,
    is_pinned: true,
    like_count: 10,
    created_at: '2024-01-03T12:00:00Z',
    updated_at: '2024-01-03T12:00:00Z',
    reply_count: 0,
    paragraph_index: null,
    selection_start: null,
    selection_end: null,
    quoted_text: '',
    parent_id: null,
  }
];

describe('CommentThread', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
    (useAuthStore as any).mockImplementation((selector: any) => selector({ user: mockUser }));
  });

  it('renders loading state initially', () => {
    (interactionsApi.getComments as any).mockReturnValue(new Promise(() => {})); 
    render(
      <QueryClientProvider client={queryClient}>
        <CommentThread chapterId={1} />
      </QueryClientProvider>
    );
    expect(screen.getByTestId('comment-skeleton')).toBeInTheDocument();
  });

  it('renders empty state when no comments', async () => {
    (interactionsApi.getComments as any).mockResolvedValue({ results: [], total: 0 });

    render(
      <QueryClientProvider client={queryClient}>
        <CommentThread chapterId={1} />
      </QueryClientProvider>
    );

    expect(await screen.findByText('댓글이 없습니다')).toBeInTheDocument();
  });

  it('renders list of comments with pinned ones at top', async () => {
    (interactionsApi.getComments as any).mockResolvedValue({ results: mockComments, total: 3 });

    render(
      <QueryClientProvider client={queryClient}>
        <CommentThread chapterId={1} />
      </QueryClientProvider>
    );

    const articles = await screen.findAllByRole('article');
    expect(articles).toHaveLength(3);
    
    // Check order: Pinned (id 3) should be first
    expect(articles[0]).toHaveTextContent('Pinned comment');
    // Check others present
    expect(screen.getByText('This is a comment')).toBeInTheDocument();
    expect(screen.getByText('My comment')).toBeInTheDocument();
  });

  it('allows creating a comment', async () => {
    (interactionsApi.getComments as any).mockResolvedValue({ results: [], total: 0 });
    (interactionsApi.createComment as any).mockResolvedValue({
      id: 4,
      user: mockUser,
      content: 'New Comment',
      created_at: new Date().toISOString(),
      like_count: 0,
      is_pinned: false,
      is_spoiler: false,
      reply_count: 0,
      parent_id: null,
      paragraph_index: null,
      selection_start: null,
      selection_end: null,
      quoted_text: ''
    });

    render(
      <QueryClientProvider client={queryClient}>
        <CommentThread chapterId={1} />
      </QueryClientProvider>
    );

    const input = await screen.findByPlaceholderText(/댓글을 작성하세요/i);
    const submitBtn = screen.getByRole('button', { name: /등록/i });

    fireEvent.change(input, { target: { value: 'New Comment' } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(interactionsApi.createComment).toHaveBeenCalledWith(1, expect.objectContaining({ content: 'New Comment' }));
    });
  });

  it('allows deleting own comment', async () => {
    (interactionsApi.getComments as any).mockResolvedValue({ results: mockComments, total: 3 });
    (interactionsApi.deleteComment as any).mockResolvedValue(undefined);

    render(
      <QueryClientProvider client={queryClient}>
        <CommentThread chapterId={1} />
      </QueryClientProvider>
    );

    // Find delete button for own comment (id 2 - "My comment")
    const myComment = await screen.findByText('My comment');
    // We assume the delete button is rendered near the comment.
    // We'll give it a specific aria-label or testid in implementation.
    const deleteBtns = screen.getAllByLabelText('Delete comment');
    // Should be only 1 because only 1 comment is owned by user
    expect(deleteBtns).toHaveLength(1);
    
    fireEvent.click(deleteBtns[0]);

    await waitFor(() => {
      expect(interactionsApi.deleteComment).toHaveBeenCalledWith(2);
    });
  });

  it('displays error message on fetch failure', async () => {
    (interactionsApi.getComments as any).mockRejectedValue(new Error('Failed to fetch'));

    render(
      <QueryClientProvider client={queryClient}>
        <CommentThread chapterId={1} />
      </QueryClientProvider>
    );

    expect(await screen.findByText(/댓글을 불러올 수 없습니다/i)).toBeInTheDocument();
  });
});

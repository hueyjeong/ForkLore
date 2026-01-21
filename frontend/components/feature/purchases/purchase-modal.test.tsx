import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { PurchaseModal } from './purchase-modal';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import * as interactionsApi from '@/lib/api/interactions.api';
import * as walletApi from '@/lib/api/wallet.api';

// Mock the API modules
vi.mock('@/lib/api/interactions.api', () => ({
  purchaseChapter: vi.fn(),
}));

vi.mock('@/lib/api/wallet.api', () => ({
  getWalletBalance: vi.fn(),
}));

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

describe('PurchaseModal', () => {
  const defaultProps = {
    chapterId: 1,
    chapterTitle: 'Test Chapter',
    price: 200,
    isOpen: true,
    onClose: vi.fn(),
    onSuccess: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly with chapter info and price', () => {
    const queryClient = createTestQueryClient();
    (walletApi.getWalletBalance as any).mockResolvedValue({ balance: 1000 });

    render(
      <QueryClientProvider client={queryClient}>
        <PurchaseModal {...defaultProps} />
      </QueryClientProvider>
    );

    expect(screen.getByText(/Test Chapter/)).toBeInTheDocument();
    expect(screen.getByText('200 코인')).toBeInTheDocument();
  });

  it('shows current balance and calculates remaining balance', async () => {
    const queryClient = createTestQueryClient();
    (walletApi.getWalletBalance as any).mockResolvedValue({ balance: 1000 });

    render(
      <QueryClientProvider client={queryClient}>
        <PurchaseModal {...defaultProps} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('1,000 코인')).toBeInTheDocument(); // Current
      expect(screen.getByText('800 코인')).toBeInTheDocument();   // Remaining
    });
  });

  it('disables confirm button when balance is insufficient', async () => {
    const queryClient = createTestQueryClient();
    (walletApi.getWalletBalance as any).mockResolvedValue({ balance: 100 }); // Less than 200

    render(
      <QueryClientProvider client={queryClient}>
        <PurchaseModal {...defaultProps} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      const confirmButton = screen.getByRole('button', { name: /구매하기/i });
      expect(confirmButton).toBeDisabled();
      expect(screen.getByText('잔액 부족')).toBeInTheDocument();
    });
  });

  it('calls purchaseChapter API and onSuccess when confirmed', async () => {
    const queryClient = createTestQueryClient();
    (walletApi.getWalletBalance as any).mockResolvedValue({ balance: 1000 });
    (interactionsApi.purchaseChapter as any).mockResolvedValue({});

    render(
      <QueryClientProvider client={queryClient}>
        <PurchaseModal {...defaultProps} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('1,000 코인')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /구매하기/i }));

    await waitFor(() => {
      expect(interactionsApi.purchaseChapter).toHaveBeenCalledWith(1);
      expect(defaultProps.onSuccess).toHaveBeenCalled();
      expect(defaultProps.onClose).toHaveBeenCalled();
    });
  });

  it('handles purchase failure', async () => {
    const queryClient = createTestQueryClient();
    (walletApi.getWalletBalance as any).mockResolvedValue({ balance: 1000 });
    (interactionsApi.purchaseChapter as any).mockRejectedValue(new Error('Failed'));

    render(
      <QueryClientProvider client={queryClient}>
        <PurchaseModal {...defaultProps} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('1,000 코인')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /구매하기/i }));

    await waitFor(() => {
      expect(interactionsApi.purchaseChapter).toHaveBeenCalled();
      expect(defaultProps.onSuccess).not.toHaveBeenCalled();
      // You might want to check for error toast or message here
    });
  });

  it('closes modal on cancel', () => {
    const queryClient = createTestQueryClient();
    (walletApi.getWalletBalance as any).mockResolvedValue({ balance: 1000 });

    render(
      <QueryClientProvider client={queryClient}>
        <PurchaseModal {...defaultProps} />
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: /취소/i }));
    expect(defaultProps.onClose).toHaveBeenCalled();
  });
});

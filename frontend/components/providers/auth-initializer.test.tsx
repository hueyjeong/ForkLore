import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import { useAuthStore } from '@/stores/auth-store';
import { AuthInitializer } from '@/components/providers/auth-initializer';

// Mock auth store
vi.mock('@/stores/auth-store', () => ({
  useAuthStore: vi.fn(),
}));

describe('AuthInitializer', () => {
  const mockRefreshUser = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useAuthStore as any).mockReturnValue(mockRefreshUser);
  });

  it('should call refreshUser on mount', () => {
    render(<AuthInitializer><div>Test</div></AuthInitializer>);

    expect(mockRefreshUser).toHaveBeenCalledTimes(1);
  });

  it('should render children', () => {
    const { getByText } = render(
      <AuthInitializer>
        <div>Test Children</div>
      </AuthInitializer>
    );

    expect(getByText('Test Children')).toBeInTheDocument();
  });

  it('should only call refreshUser once', () => {
    const { rerender } = render(<AuthInitializer><div>Test</div></AuthInitializer>);

    expect(mockRefreshUser).toHaveBeenCalledTimes(1);

    // Rerender should not call refreshUser again
    rerender(<AuthInitializer><div>Updated</div></AuthInitializer>);
    expect(mockRefreshUser).toHaveBeenCalledTimes(1);
  });
});

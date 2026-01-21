
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SpoilerAlert } from './spoiler-alert';
import * as ReadingProgressHook from '@/hooks/use-reading-progress';

// Mock the hook
vi.mock('@/hooks/use-reading-progress', () => ({
  useReadingProgress: vi.fn(),
}));

describe('SpoilerAlert', () => {
  const defaultProps = {
    spoilerChapter: 10,
    novelId: 1,
    children: <div>Spoiler Content</div>,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows content when chapter is not a spoiler (current >= spoiler)', () => {
    vi.mocked(ReadingProgressHook.useReadingProgress).mockReturnValue({
      currentChapterNumber: 15, // User read past the spoiler
      isLoading: false,
      error: null,
      recordProgress: vi.fn(),
    });

    render(<SpoilerAlert {...defaultProps} />);
    
    expect(screen.getByText('Spoiler Content')).toBeVisible();
    expect(screen.queryByText('스포일러 보기')).not.toBeInTheDocument();
  });

  it('blurs content and shows button when chapter is a spoiler (current < spoiler)', () => {
    vi.mocked(ReadingProgressHook.useReadingProgress).mockReturnValue({
      currentChapterNumber: 5, // User hasn't reached the spoiler
      isLoading: false,
      error: null,
      recordProgress: vi.fn(),
    });

    render(<SpoilerAlert {...defaultProps} />);
    
    // Content should be present but we check for the button
    expect(screen.getByText('스포일러 보기')).toBeVisible();
    // We can't easily check for CSS blur in jsdom, but we can check if the button is there
    // and maybe check for a class on a container
  });

  it('reveals content on button click', () => {
    vi.mocked(ReadingProgressHook.useReadingProgress).mockReturnValue({
      currentChapterNumber: 5,
      isLoading: false,
      error: null,
      recordProgress: vi.fn(),
    });

    render(<SpoilerAlert {...defaultProps} />);
    
    const button = screen.getByText('스포일러 보기');
    fireEvent.click(button);
    
    expect(button).not.toBeVisible(); // Button should disappear or change
    expect(screen.getByText('Spoiler Content')).toBeVisible();
  });

  it('shows blur (safe default) during loading', () => {
    vi.mocked(ReadingProgressHook.useReadingProgress).mockReturnValue({
      currentChapterNumber: null,
      isLoading: true,
      error: null,
      recordProgress: vi.fn(),
    });

    render(<SpoilerAlert {...defaultProps} />);
    
    // Should show blur/button (safe default)
    expect(screen.getByText('스포일러 보기')).toBeVisible();
  });

  it('shows blur (safe default) on error', () => {
    vi.mocked(ReadingProgressHook.useReadingProgress).mockReturnValue({
      currentChapterNumber: null,
      isLoading: false,
      error: new Error('Failed to fetch'),
      recordProgress: vi.fn(),
    });

    render(<SpoilerAlert {...defaultProps} />);
    
    // Should show blur/button
    expect(screen.getByText('스포일러 보기')).toBeVisible();
  });

  it('shows content when not authenticated (currentChapterNumber is null and not loading/error)', () => {
    vi.mocked(ReadingProgressHook.useReadingProgress).mockReturnValue({
      currentChapterNumber: null,
      isLoading: false,
      error: null,
      recordProgress: vi.fn(),
    });

    render(<SpoilerAlert {...defaultProps} />);
    
    // Should show content without spoiler protection
    expect(screen.getByText('Spoiler Content')).toBeVisible();
    expect(screen.queryByText('스포일러 보기')).not.toBeInTheDocument();
  });
});

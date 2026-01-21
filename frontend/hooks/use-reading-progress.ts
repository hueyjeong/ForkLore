import { useMutation } from '@tanstack/react-query';
import { recordReadingProgress } from '@/lib/api/chapters.api';

interface UseReadingProgressReturn {
  currentChapterNumber: number | null;
  recordProgress: (chapterId: number, progress: number) => Promise<void>;
  isLoading: boolean;
  error: Error | null;
}

export function useReadingProgress(
  novelId?: number
): UseReadingProgressReturn {
  const mutation = useMutation({
    mutationFn: ({ chapterId, progress }: { chapterId: number; progress: number }) =>
      recordReadingProgress(chapterId, progress),
  });

  const recordProgress = async (chapterId: number, progress: number): Promise<void> => {
    await mutation.mutateAsync({ chapterId, progress });
  };

  return {
    currentChapterNumber: null,
    recordProgress,
    isLoading: mutation.isPending,
    error: mutation.error,
  };
}

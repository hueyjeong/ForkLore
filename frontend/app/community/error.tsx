'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { AlertCircle } from 'lucide-react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Community page error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center space-y-4 max-w-md px-4">
        <div className="flex justify-center">
          <AlertCircle className="h-16 w-16 text-destructive" />
        </div>
        <h2 className="text-2xl font-bold">오류가 발생했습니다</h2>
        <p className="text-muted-foreground">
          커뮤니티 페이지를 불러오는 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.
        </p>
        <Button onClick={reset} variant="default">
          다시 시도
        </Button>
        <div className="pt-4 border-t">
          <p className="text-sm text-muted-foreground">
            문제가 지속되면 고객센터에 문의해주세요.
          </p>
        </div>
      </div>
    </div>
  );
}

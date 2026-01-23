'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="max-w-md text-center space-y-6 p-8">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold text-foreground">Something went wrong!</h2>
          <p className="text-muted-foreground">
            {error.message || 'Failed to load novel details. Please try again.'}
          </p>
        </div>
        <div className="flex gap-4 justify-center">
          <button
            onClick={reset}
            className="rounded-lg bg-primary px-6 py-3 text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
          >
            Try again
          </button>
          <a
            href="/"
            className="rounded-lg border border-border px-6 py-3 text-foreground font-medium hover:bg-accent transition-colors"
          >
            Go home
          </a>
        </div>
      </div>
    </div>
  );
}

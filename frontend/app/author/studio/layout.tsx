'use client';

import { useQuery } from '@tanstack/react-query';
import { getMyProfile } from '@/lib/api/auth.api';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect } from 'react';
import { Loader2, LayoutDashboard } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

export default function AuthorStudioLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { data: user, isPending, isError } = useQuery({
    queryKey: ['myProfile'],
    queryFn: getMyProfile,
    retry: false,
  });

  useEffect(() => {
    if (isError) {
      router.push('/login');
    }
    if (!isPending && user) {
      if (user.role !== 'AUTHOR') {
        router.push('/');
        // Optionally show toast "Author access only"
      }
    }
  }, [user, isPending, isError, router]);

  if (isPending) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!user || user.role !== 'AUTHOR') {
    return null;
  }

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="w-64 border-r bg-muted/10 hidden md:block fixed inset-y-0 pt-16">
        <div className="p-6">
          <h2 className="text-xl font-bold tracking-tight mb-6">Author Studio</h2>
          <nav className="space-y-2">
            <Link
              href="/author/studio"
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-md transition-colors font-medium',
                pathname === '/author/studio'
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </Link>
          </nav>
        </div>
      </aside>
      <main className="flex-1 md:pl-64 pt-6">
        <div className="container mx-auto p-6 max-w-6xl">{children}</div>
      </main>
    </div>
  );
}

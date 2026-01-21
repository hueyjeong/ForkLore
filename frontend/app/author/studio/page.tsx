'use client';

import { useQuery } from '@tanstack/react-query';
import { getMyProfile } from '@/lib/api/auth.api';
import { getNovels } from '@/lib/api/novels.api';
import { getLinkRequests } from '@/lib/api/branches.api';
import { Novel } from '@/types/novels.types';
import { BranchLinkRequest } from '@/types/branches.types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { BookOpen, FileText, Eye, GitPullRequest } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function AuthorStudioPage() {
  const { data: user } = useQuery({
    queryKey: ['myProfile'],
    queryFn: getMyProfile,
  });

  const { data: novelsData, isPending: isNovelsPending } = useQuery({
    queryKey: ['myNovels', user?.id],
    queryFn: () => getNovels({ author_id: user?.id, limit: 100 }),
    enabled: !!user?.id,
  });

  const { data: requestsData, isPending: isRequestsPending } = useQuery({
    queryKey: ['linkRequests'],
    queryFn: () => getLinkRequests(),
    enabled: !!user?.id,
  });

  const novels = novelsData?.results || [];
  const requests = requestsData?.results || [];

  // Calculate stats
  const totalNovels = novelsData?.total || 0;
  const totalChapters = novels.reduce((acc: number, novel: Novel) => acc + (novel.total_chapter_count || 0), 0);
  const totalViews = novels.reduce((acc: number, novel: Novel) => acc + (novel.total_view_count || 0), 0);
  const pendingRequests = requests.filter((r: BranchLinkRequest) => r.status === 'PENDING').length;

  if (isNovelsPending || isRequestsPending) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Author Studio</h1>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  <Skeleton className="h-4 w-20" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-10" />
              </CardContent>
            </Card>
          ))}
        </div>
        <div className="grid gap-6 md:grid-cols-2">
           <Skeleton className="h-[300px]" />
           <Skeleton className="h-[300px]" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Author Studio</h1>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Novels</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalNovels}</div>
            <p className="text-xs text-muted-foreground">Published works</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Chapters</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalChapters}</div>
            <p className="text-xs text-muted-foreground">Across all novels</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Views</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalViews.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Lifetime reads</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Requests</CardTitle>
            <GitPullRequest className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pendingRequests}</div>
            <p className="text-xs text-muted-foreground">Link requests to review</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* My Novels List */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>My Novels</CardTitle>
            <CardDescription>Manage your recent works</CardDescription>
          </CardHeader>
          <CardContent>
            {novels.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center text-muted-foreground">
                <p>No novels found</p>
                <Button variant="link" asChild className="mt-2">
                  <Link href="/author/studio">Create your first novel</Link>
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {novels.slice(0, 5).map((novel: Novel) => (
                  <div key={novel.id} className="flex items-center justify-between p-2 hover:bg-muted/50 rounded-lg transition-colors">
                    <div className="flex flex-col">
                      <Link href={`/novels/${novel.id}`} className="font-medium hover:underline">
                        {novel.title}
                      </Link>
                      <span className="text-xs text-muted-foreground">
                        {new Date(novel.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                         <Badge variant={novel.status === 'ONGOING' ? 'default' : 'secondary'}>
                            {novel.status}
                         </Badge>
                    </div>
                  </div>
                ))}
                {novels.length > 5 && (
                    <Button variant="ghost" className="w-full text-xs" asChild>
                        <Link href="/author/studio/novels">View All</Link>
                    </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Link Requests List */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Link Requests</CardTitle>
            <CardDescription>Recent branch link requests</CardDescription>
          </CardHeader>
          <CardContent>
            {requests.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center text-muted-foreground">
                <p>No pending requests</p>
              </div>
            ) : (
              <div className="space-y-4">
                {requests.slice(0, 5).map((req: BranchLinkRequest) => (
                  <div key={req.id} className="flex flex-col space-y-1 p-3 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm">Request #{req.id}</span>
                      <Badge variant={req.status === 'PENDING' ? 'outline' : 'secondary'}>
                        {req.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {req.request_message || "No message"}
                    </p>
                    <div className="text-xs text-muted-foreground pt-2">
                      {new Date(req.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}


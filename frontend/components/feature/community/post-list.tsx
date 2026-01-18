import { PostCard } from './post-card';
import type { CommunityPost } from '@/lib/mock-data';

interface PostListProps {
  posts: CommunityPost[];
}

export function PostList({ posts }: PostListProps) {
  // Sort: pinned posts first, then by createdAt descending
  const sortedPosts = [...posts].sort((a, b) => {
    if (a.isPinned && !b.isPinned) return -1;
    if (!a.isPinned && b.isPinned) return 1;
    return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
  });

  if (posts.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-muted-foreground">
        게시글이 없습니다
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {sortedPosts.map((post) => (
        <article key={post.id}>
          <PostCard post={post} />
        </article>
      ))}
    </div>
  );
}

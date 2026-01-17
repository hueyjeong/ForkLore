import { Pin, MessageCircle, Heart } from 'lucide-react';
import type { CommunityPost } from '@/lib/mock-data';

interface PostCardProps {
  post: CommunityPost;
}

export function PostCard({ post }: PostCardProps) {
  return (
    <div className="flex items-start gap-4 p-4 border rounded-lg bg-card text-card-foreground shadow-sm hover:border-primary/50 transition-colors">
      {post.isPinned && (
        <Pin
          className="h-4 w-4 shrink-0 text-primary"
          data-testid="pin-icon"
        />
      )}
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground px-2 py-0.5 bg-muted rounded">
            {post.category}
          </span>
          <h3 className="font-bold text-foreground truncate">
            {post.title}
          </h3>
        </div>
        
        <div className="mt-2 flex items-center gap-4 text-sm text-muted-foreground">
          <span>{post.author}</span>
          <span>{post.createdAt}</span>
          <div className="flex items-center gap-1">
            <MessageCircle className="h-4 w-4" />
            <span>{post.commentCount}</span>
          </div>
          <div className="flex items-center gap-1">
            <Heart className="h-4 w-4" />
            <span>{post.likeCount}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

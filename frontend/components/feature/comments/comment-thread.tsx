"use client"

import * as React from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Heart, Pin, Trash2, MessageSquare, AlertTriangle, Send } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Label } from "@/components/ui/label"
import { useAuthStore } from "@/stores/auth-store"
import { getComments, createComment, deleteComment } from "@/lib/api/interactions.api"
import { CommentCreate } from "@/types/interactions.types"
import { cn } from "@/lib/utils"

interface CommentThreadProps {
  chapterId: number
}

const commentSchema = z.object({
  content: z.string().min(1, "댓글 내용을 입력해주세요").max(1000, "댓글은 1000자 이내로 작성해주세요"),
  is_spoiler: z.boolean(),
})

type CommentFormData = z.infer<typeof commentSchema>

function formatTimeAgo(dateString: string) {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (seconds < 60) return '방금 전';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}분 전`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}시간 전`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}일 전`;
  return date.toLocaleDateString('ko-KR');
}

export function CommentThread({ chapterId }: CommentThreadProps) {
  const user = useAuthStore(state => state.user)
  const queryClient = useQueryClient()
  
  // Local state for optimistic likes
  const [likedComments, setLikedComments] = React.useState<Record<number, boolean>>({})

  const { data, isLoading, error } = useQuery({
    queryKey: ['comments', chapterId],
    queryFn: () => getComments(chapterId),
  })

  const form = useForm<CommentFormData>({
    resolver: zodResolver(commentSchema),
    defaultValues: {
      content: "",
      is_spoiler: false,
    },
  })

  const createMutation = useMutation({
    mutationFn: (data: CommentCreate) => createComment(chapterId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', chapterId] })
      form.reset()
      toast.success("댓글이 등록되었습니다")
    },
    onError: () => {
      toast.error("댓글 등록에 실패했습니다")
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (commentId: number) => deleteComment(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', chapterId] })
      toast.success("댓글이 삭제되었습니다")
    },
    onError: () => {
      toast.error("댓글 삭제에 실패했습니다")
    },
  })

  const handleLike = (commentId: number) => {
    setLikedComments(prev => ({
      ...prev,
      [commentId]: !prev[commentId]
    }))
  }

  const onSubmit = (data: CommentFormData) => {
    if (!user) {
      toast.error("로그인이 필요합니다")
      return
    }
    createMutation.mutate(data)
  }

  const sortedComments = React.useMemo(() => {
    // Fix: Access property 'results' instead of 'items' based on PaginatedResponse type
    if (!data?.results) return []
    return [...data.results].sort((a, b) => {
      if (a.is_pinned && !b.is_pinned) return -1
      if (!a.is_pinned && b.is_pinned) return 1
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    })
  }, [data?.results])

  if (isLoading) {
    return (
      <div className="space-y-4" data-testid="comment-skeleton">
        <Skeleton className="h-24 w-full" />
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex gap-4">
              <Skeleton className="h-10 w-10 rounded-full" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-4 w-[200px]" />
                <Skeleton className="h-16 w-full" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          댓글을 불러올 수 없습니다. 다시 시도해주세요.
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <MessageSquare className="h-5 w-5" />
          댓글 <span className="text-muted-foreground">{data?.total || 0}</span>
        </h3>
      </div>

      {/* Write Form */}
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <div className="flex gap-4">
          <Avatar className="h-10 w-10">
            {/* Fix: use profileImageUrl for UserResponse (Auth user) */}
            <AvatarImage src={user?.profileImageUrl || undefined} />
            <AvatarFallback>{user?.nickname?.[0] || "?"}</AvatarFallback>
          </Avatar>
          <div className="flex-1 space-y-2">
            <Textarea
              placeholder={user ? "댓글을 작성하세요..." : "로그인이 필요합니다"}
              disabled={!user || createMutation.isPending}
              className="min-h-[100px] resize-none"
              {...form.register("content")}
            />
            {form.formState.errors.content && (
              <p className="text-sm text-destructive">{form.formState.errors.content.message}</p>
            )}
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is_spoiler"
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  {...form.register("is_spoiler")}
                  disabled={!user || createMutation.isPending}
                />
                <Label htmlFor="is_spoiler" className="text-sm text-muted-foreground cursor-pointer">
                  스포일러 포함
                </Label>
              </div>
              <Button 
                type="submit" 
                size="sm" 
                disabled={!user || createMutation.isPending}
              >
                {createMutation.isPending ? "등록 중..." : "등록"}
                {!createMutation.isPending && <Send className="ml-2 h-4 w-4" />}
              </Button>
            </div>
          </div>
        </div>
      </form>

      {/* Comment List */}
      <div className="space-y-6">
        {sortedComments.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            댓글이 없습니다
          </div>
        ) : (
          sortedComments.map((comment) => (
            <article key={comment.id} className="group flex gap-4 animate-in fade-in slide-in-from-bottom-2">
              <Avatar className="h-10 w-10 mt-1">
                {/* Fix: use profile_image for UserBrief (Comment author) */}
                <AvatarImage src={comment.user.profile_image || undefined} />
                <AvatarFallback>{comment.user.nickname[0]}</AvatarFallback>
              </Avatar>
              <div className="flex-1 space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm">{comment.user.nickname}</span>
                    <span className="text-xs text-muted-foreground">
                      {formatTimeAgo(comment.created_at)}
                    </span>
                    {comment.is_pinned && (
                      <Badge variant="secondary" className="h-5 text-[10px] gap-1 px-1.5">
                        <Pin className="h-3 w-3" /> 고정됨
                      </Badge>
                    )}
                  </div>
                  {user?.id === comment.user.id && (
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={() => deleteMutation.mutate(comment.id)}
                      disabled={deleteMutation.isPending}
                      aria-label="Delete comment"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
                
                <div className={cn("text-sm leading-relaxed whitespace-pre-wrap mt-1", 
                  comment.is_spoiler && "blur-sm hover:blur-none transition-all duration-300 cursor-pointer relative"
                )}>
                  {comment.is_spoiler && (
                    <div className="absolute inset-0 flex items-center justify-center text-xs text-muted-foreground pointer-events-none hover:hidden">
                      스포일러가 포함된 댓글입니다 (클릭하여 보기)
                    </div>
                  )}
                  {comment.content}
                </div>

                <div className="flex items-center gap-4 pt-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className={cn("h-8 px-2 text-muted-foreground hover:text-red-500 hover:bg-red-50", 
                      likedComments[comment.id] && "text-red-500 bg-red-50"
                    )}
                    onClick={() => handleLike(comment.id)}
                  >
                    <Heart className={cn("h-4 w-4 mr-1.5", likedComments[comment.id] && "fill-current")} />
                    <span className="text-xs">
                      {comment.like_count + (likedComments[comment.id] ? 1 : 0)}
                    </span>
                  </Button>
                </div>
              </div>
            </article>
          ))
        )}
      </div>
    </div>
  )
}

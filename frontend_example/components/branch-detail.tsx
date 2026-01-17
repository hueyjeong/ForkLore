"use client"

import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { GitBranch, TrendingUp, Eye, Heart, MessageSquare, Share2, BookOpen, ChevronLeft, Star } from "lucide-react"

interface BranchDetailProps {
  branchId: string
}

export function BranchDetail({ branchId }: BranchDetailProps) {
  // Mock data
  const branch = {
    id: branchId,
    title: "IF: 흑마법사가 백마법을 배웠다면",
    description:
      "에스테반이 회귀 후 흑마법 대신 백마법의 길을 선택한다면? 완전히 다른 스토리가 펼쳐집니다. 신성한 마법으로 세상을 구하려는 에스테반의 이야기.",
    originalNovel: "흑마법사의 회귀",
    originalNovelId: "1",
    author: "팬작가A",
    authorId: "fan123",
    forkPoint: 5,
    forkChapterTitle: "첫 번째 선택",
    chapters: 15,
    votes: 1234,
    views: 8934,
    likes: 543,
    comments: 234,
    status: "연재중",
    createdAt: "2주 전",
    lastUpdate: "1일 전",
    mergeStatus: "candidate",
    mergeThreshold: 1500,
    coverImage: "/placeholder.svg?height=400&width=300",
  }

  const recentChapters = [
    { chapter: 15, title: "백마법의 진수", date: "1일 전", views: 234 },
    { chapter: 14, title: "신성한 힘", date: "3일 전", views: 312 },
    { chapter: 13, title: "빛의 수호자", date: "5일 전", views: 289 },
  ]

  const progress = (branch.votes / branch.mergeThreshold) * 100

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-6">
        <Link href="/branches" className="text-sm text-muted-foreground hover:text-primary">
          브랜치
        </Link>
        <span className="text-muted-foreground">/</span>
        <span className="text-sm font-medium">{branch.title}</span>
      </div>

      {/* Branch Header */}
      <section className="bg-gradient-to-b from-accent/5 to-background rounded-lg p-8 mb-8">
        <div className="grid md:grid-cols-[280px_1fr] gap-8">
          <div className="mx-auto md:mx-0">
            <div className="aspect-[3/4] w-full max-w-[280px] rounded-lg overflow-hidden shadow-lg">
              <img
                src={branch.coverImage || "/placeholder.svg"}
                alt={branch.title}
                className="w-full h-full object-cover"
              />
            </div>
          </div>

          <div className="space-y-6">
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline" className="gap-1">
                  <GitBranch className="h-3 w-3" />
                  브랜치
                </Badge>
                {branch.mergeStatus === "candidate" && (
                  <Badge className="gap-1">
                    <Star className="h-3 w-3" />
                    정사 편입 후보
                  </Badge>
                )}
                <Badge variant="outline">{branch.status}</Badge>
              </div>
              <h1 className="font-serif text-3xl md:text-4xl font-bold">{branch.title}</h1>
              <div className="flex flex-col gap-2 text-muted-foreground">
                <div>
                  원작:{" "}
                  <Link href={`/novel/${branch.originalNovelId}`} className="hover:text-primary font-medium">
                    {branch.originalNovel}
                  </Link>
                </div>
                <div>
                  {branch.forkPoint}화 "{branch.forkChapterTitle}"에서 분기
                </div>
                <div>
                  작가:{" "}
                  <Link href={`/author/${branch.authorId}`} className="hover:text-primary font-medium">
                    {branch.author}
                  </Link>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-6 text-sm">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
                <span>
                  추천 <strong className="text-foreground">{branch.votes.toLocaleString()}</strong>
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Eye className="h-4 w-4 text-muted-foreground" />
                <span>
                  조회 <strong className="text-foreground">{branch.views.toLocaleString()}</strong>
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Heart className="h-4 w-4 text-muted-foreground" />
                <span>
                  좋아요 <strong className="text-foreground">{branch.likes.toLocaleString()}</strong>
                </span>
              </div>
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
                <span>
                  댓글 <strong className="text-foreground">{branch.comments.toLocaleString()}</strong>
                </span>
              </div>
            </div>

            <p className="text-muted-foreground leading-relaxed">{branch.description}</p>

            <div className="flex flex-wrap gap-3">
              <Button size="lg" asChild>
                <Link href={`/branch/${branch.id}/read/1`}>
                  <BookOpen className="mr-2 h-4 w-4" />첫 화부터 읽기
                </Link>
              </Button>
              <Button size="lg" variant="outline">
                <TrendingUp className="mr-2 h-4 w-4" />
                추천하기
              </Button>
              <Button size="lg" variant="outline">
                <Heart className="mr-2 h-4 w-4" />
                좋아요
              </Button>
              <Button size="lg" variant="outline">
                <Share2 className="mr-2 h-4 w-4" />
                공유
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Merge Progress */}
      {branch.mergeStatus === "candidate" && (
        <Card className="mb-8 bg-gradient-to-br from-primary/5 to-background border-primary/20">
          <CardContent className="p-6">
            <div className="flex items-start gap-3 mb-4">
              <Star className="h-6 w-6 text-primary shrink-0" />
              <div className="flex-1">
                <h3 className="font-semibold mb-1">정사 편입 진행 상황</h3>
                <p className="text-sm text-muted-foreground">
                  목표 추천 수 {branch.mergeThreshold}개 중 {branch.votes}개 달성
                </p>
              </div>
            </div>
            <div className="space-y-2">
              <div className="h-3 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${progress}%` }} />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{Math.round(progress)}% 달성</span>
                <span>{branch.mergeThreshold - branch.votes}개 남음</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid lg:grid-cols-[1fr_320px] gap-8">
        {/* Main Content */}
        <div className="space-y-6">
          {/* Recent Chapters */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-serif text-2xl font-bold">최근 회차</h2>
                <Link href={`/branch/${branch.id}/chapters`} className="text-sm text-primary hover:underline">
                  전체보기
                </Link>
              </div>
              <div className="space-y-1">
                {recentChapters.map((chapter) => (
                  <Link
                    key={chapter.chapter}
                    href={`/branch/${branch.id}/read/${chapter.chapter}`}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors group"
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <span className="text-sm font-medium text-muted-foreground shrink-0">{chapter.chapter}화</span>
                      <span className="font-medium truncate group-hover:text-primary transition-colors">
                        {chapter.title}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground shrink-0 ml-4">
                      <span className="hidden sm:inline">{chapter.date}</span>
                      <span className="flex items-center gap-1">
                        <Eye className="h-3 w-3" />
                        {chapter.views}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Branch Info */}
          <Card>
            <CardContent className="p-6">
              <h2 className="font-serif text-2xl font-bold mb-4">브랜치 정보</h2>
              <div className="space-y-4 text-sm">
                <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/30">
                  <GitBranch className="h-5 w-5 text-accent shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold mb-1">분기 지점</h4>
                    <p className="text-muted-foreground leading-relaxed">
                      원작 {branch.originalNovel}의 {branch.forkPoint}화 "{branch.forkChapterTitle}"에서 분기되었습니다.
                      이 지점까지의 설정과 세계관을 그대로 상속받습니다.
                    </p>
                    <Button variant="outline" size="sm" className="mt-2 bg-transparent" asChild>
                      <Link href={`/novel/${branch.originalNovelId}/read/${branch.forkPoint}`}>분기 지점 보기</Link>
                    </Button>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/30">
                  <BookOpen className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold mb-1">상속된 세계관</h4>
                    <p className="text-muted-foreground leading-relaxed">
                      이 브랜치는 분기 시점까지의 위키 정보, 지도, 등장인물 관계도를 모두 상속받습니다. 작가는 이를
                      바탕으로 새로운 이야기를 전개합니다.
                    </p>
                    <Button variant="outline" size="sm" className="mt-2 bg-transparent" asChild>
                      <Link href={`/branch/${branch.id}/wiki`}>브랜치 위키 보기</Link>
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Author Info */}
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-4">작가 정보</h3>
              <div className="flex items-center gap-3 mb-4">
                <div className="h-12 w-12 rounded-full bg-accent/10 flex items-center justify-center">
                  <span className="font-semibold text-accent">팬</span>
                </div>
                <div>
                  <Link href={`/author/${branch.authorId}`} className="font-medium hover:text-primary">
                    {branch.author}
                  </Link>
                  <p className="text-xs text-muted-foreground">브랜치 작가</p>
                </div>
              </div>
              <Button variant="outline" className="w-full bg-transparent">
                작가 팔로우
              </Button>
            </CardContent>
          </Card>

          {/* Original Novel */}
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-4">원작 작품</h3>
              <Link href={`/novel/${branch.originalNovelId}`} className="block group">
                <div className="aspect-[3/4] rounded-lg bg-muted overflow-hidden mb-3">
                  <img
                    src="/dark-fantasy-wizard.jpg"
                    alt={branch.originalNovel}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                  />
                </div>
                <h4 className="font-serif font-semibold group-hover:text-primary transition-colors">
                  {branch.originalNovel}
                </h4>
                <p className="text-xs text-muted-foreground mt-1">원작 보러가기</p>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Back Button */}
      <div className="mt-8">
        <Button variant="outline" asChild>
          <Link href="/branches">
            <ChevronLeft className="mr-2 h-4 w-4" />
            브랜치 목록으로
          </Link>
        </Button>
      </div>
    </div>
  )
}

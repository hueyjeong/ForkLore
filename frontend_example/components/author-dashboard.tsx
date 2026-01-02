"use client"

import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { BookOpen, Plus, Eye, Heart, MessageSquare, Edit, Settings, Sparkles } from "lucide-react"

export function AuthorDashboard() {
  // Mock data
  const novels = [
    {
      id: "1",
      title: "흑마법사의 회귀",
      status: "연재중",
      chapters: 245,
      totalViews: 125430,
      totalLikes: 2340,
      totalComments: 5678,
      lastUpdate: "2시간 전",
      branches: 23,
      coverImage: "/dark-fantasy-wizard.jpg",
    },
    {
      id: "2",
      title: "별을 삼킨 마왕",
      status: "연재중",
      chapters: 156,
      totalViews: 89200,
      totalLikes: 1820,
      totalComments: 3421,
      lastUpdate: "1일 전",
      branches: 12,
      coverImage: "/demon-king-stars.jpg",
    },
  ]

  const recentChapters = [
    {
      novelTitle: "흑마법사의 회귀",
      chapter: 245,
      title: "어둠의 심연에서",
      views: 1234,
      likes: 89,
      comments: 45,
      status: "발행됨",
    },
    {
      novelTitle: "별을 삼킨 마왕",
      chapter: 156,
      title: "우주의 끝에서",
      views: 892,
      likes: 67,
      comments: 32,
      status: "발행됨",
    },
  ]

  const stats = {
    totalNovels: 2,
    totalChapters: 401,
    totalViews: 214630,
    totalFollowers: 8934,
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-serif text-3xl md:text-4xl font-bold mb-4">작가 스튜디오</h1>
        <p className="text-muted-foreground">AI 코파일럿과 함께 완벽한 세계관을 구축하세요</p>
      </div>

      {/* Quick Stats */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">작품 수</p>
                <p className="text-2xl font-bold">{stats.totalNovels}</p>
              </div>
              <BookOpen className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">총 회차</p>
                <p className="text-2xl font-bold">{stats.totalChapters}</p>
              </div>
              <Edit className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">총 조회수</p>
                <p className="text-2xl font-bold">{stats.totalViews.toLocaleString()}</p>
              </div>
              <Eye className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">팔로워</p>
                <p className="text-2xl font-bold">{stats.totalFollowers.toLocaleString()}</p>
              </div>
              <Heart className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* My Novels */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-serif text-2xl font-bold">내 작품</h2>
          <Button asChild>
            <Link href="/studio/new">
              <Plus className="mr-2 h-4 w-4" />새 작품 시작하기
            </Link>
          </Button>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {novels.map((novel) => (
            <Card key={novel.id} className="hover:shadow-md transition-shadow">
              <div className="flex gap-4 p-6">
                <div className="w-24 h-32 rounded-lg overflow-hidden bg-muted shrink-0">
                  <img
                    src={novel.coverImage || "/placeholder.svg"}
                    alt={novel.title}
                    className="w-full h-full object-cover"
                  />
                </div>

                <div className="flex-1 min-w-0 space-y-3">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant={novel.status === "연재중" ? "default" : "secondary"}>{novel.status}</Badge>
                      <Badge variant="outline" className="gap-1">
                        <Sparkles className="h-3 w-3" />
                        브랜치 {novel.branches}
                      </Badge>
                    </div>
                    <h3 className="font-serif text-xl font-bold truncate">{novel.title}</h3>
                    <p className="text-sm text-muted-foreground">총 {novel.chapters}화</p>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Eye className="h-3 w-3" />
                      {novel.totalViews.toLocaleString()}
                    </div>
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Heart className="h-3 w-3" />
                      {novel.totalLikes.toLocaleString()}
                    </div>
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <MessageSquare className="h-3 w-3" />
                      {novel.totalComments.toLocaleString()}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button size="sm" asChild>
                      <Link href={`/studio/write/${novel.id}`}>
                        <Edit className="mr-2 h-3 w-3" />새 회차 작성
                      </Link>
                    </Button>
                    <Button size="sm" variant="outline" asChild>
                      <Link href={`/studio/manage/${novel.id}`}>
                        <Settings className="mr-2 h-3 w-3" />
                        관리
                      </Link>
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Recent Chapters */}
      <div>
        <h2 className="font-serif text-2xl font-bold mb-6">최근 회차</h2>
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              {recentChapters.map((chapter, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm text-muted-foreground">{chapter.novelTitle}</span>
                      <Badge variant="outline" className="text-xs">
                        {chapter.chapter}화
                      </Badge>
                    </div>
                    <h4 className="font-medium truncate">{chapter.title}</h4>
                  </div>
                  <div className="flex items-center gap-4 ml-4 shrink-0 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Eye className="h-3 w-3" />
                      {chapter.views}
                    </span>
                    <span className="flex items-center gap-1">
                      <Heart className="h-3 w-3" />
                      {chapter.likes}
                    </span>
                    <span className="flex items-center gap-1">
                      <MessageSquare className="h-3 w-3" />
                      {chapter.comments}
                    </span>
                    <Button size="sm" variant="ghost" asChild>
                      <Link href={`/studio/write/${index + 1}/edit/${chapter.chapter}`}>수정</Link>
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Assistant CTA */}
      <Card className="mt-8 bg-gradient-to-br from-accent/10 to-background border-accent/20">
        <CardContent className="p-8 text-center">
          <Sparkles className="h-12 w-12 text-accent mx-auto mb-4" />
          <h3 className="font-serif text-2xl font-bold mb-2">AI 코파일럿으로 더 쉽게 창작하세요</h3>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            위키 자동 생성, 세계관 일관성 검사, 문장 다듬기 등 AI가 작가님의 창작을 도와드립니다
          </p>
          <Button size="lg" variant="outline" className="bg-transparent">
            <Sparkles className="mr-2 h-4 w-4" />
            AI 기능 살펴보기
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

"use client"

import { useState } from "react"
import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Search, GitBranch, TrendingUp, Clock, Star, Eye, ChevronRight } from "lucide-react"

export function BranchExplorer() {
  const [searchQuery, setSearchQuery] = useState("")

  // Mock data
  const branches = [
    {
      id: "1",
      title: "IF: 흑마법사가 백마법을 배웠다면",
      description: "에스테반이 회귀 후 흑마법 대신 백마법의 길을 선택한다면? 완전히 다른 스토리가 펼쳐집니다.",
      originalNovel: "흑마법사의 회귀",
      originalNovelId: "1",
      author: "팬작가A",
      authorId: "fan123",
      forkPoint: 5,
      chapters: 15,
      votes: 1234,
      views: 8934,
      status: "연재중",
      createdAt: "2주 전",
      lastUpdate: "1일 전",
      mergeStatus: "candidate",
      coverImage: "/placeholder.svg?height=200&width=150",
    },
    {
      id: "2",
      title: "IF: 검이 아닌 마법을 선택했다면",
      description: "제국의 검사가 마법사의 길을 걸었다면 어떤 이야기가 펼쳐질까요?",
      originalNovel: "제국의 검",
      originalNovelId: "2",
      author: "팬작가B",
      authorId: "fan456",
      forkPoint: 12,
      chapters: 23,
      votes: 892,
      views: 6541,
      status: "연재중",
      createdAt: "1달 전",
      lastUpdate: "3일 전",
      mergeStatus: "reviewing",
      coverImage: "/placeholder.svg?height=200&width=150",
    },
    {
      id: "3",
      title: "IF: 마왕이 인간 편이 되었다면",
      description: "별을 삼킨 마왕이 인간의 편에 서서 싸운다면?",
      originalNovel: "별을 삼킨 마왕",
      originalNovelId: "3",
      author: "팬작가C",
      authorId: "fan789",
      forkPoint: 34,
      chapters: 12,
      votes: 756,
      views: 4892,
      status: "연재중",
      createdAt: "3주 전",
      lastUpdate: "5일 전",
      mergeStatus: null,
      coverImage: "/placeholder.svg?height=200&width=150",
    },
  ]

  const mergedBranches = [
    {
      id: "m1",
      title: "IF: 시간여행자가 미래를 선택했다면",
      originalNovel: "시간을 거스르는 자",
      author: "팬작가D",
      mergedAt: "1주 전",
      mergedChapter: 178,
      votes: 2341,
      status: "정사 편입됨",
    },
    {
      id: "m2",
      title: "IF: 두 번째 회귀",
      originalNovel: "흑마법사의 회귀",
      author: "팬작가E",
      mergedAt: "2주 전",
      mergedChapter: 89,
      votes: 1876,
      status: "정사 편입됨",
    },
  ]

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <GitBranch className="h-8 w-8 text-accent" />
          <h1 className="font-serif text-3xl md:text-4xl font-bold">브랜치 탐색</h1>
        </div>
        <p className="text-muted-foreground max-w-2xl leading-relaxed">
          원작에서 분기된 IF 스토리를 탐험하세요. 독자가 만든 브랜치가 작가의 승인을 받으면 정사로 편입됩니다.
        </p>
      </div>

      {/* Search */}
      <div className="relative mb-8">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="search"
          placeholder="브랜치 제목, 원작, 작가 검색..."
          className="pl-9"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Content */}
      <Tabs defaultValue="active" className="space-y-6">
        <TabsList>
          <TabsTrigger value="active">활성 브랜치</TabsTrigger>
          <TabsTrigger value="merged">정사 편입</TabsTrigger>
          <TabsTrigger value="trending">인기순</TabsTrigger>
        </TabsList>

        {/* Active Branches */}
        <TabsContent value="active" className="space-y-4">
          {branches.map((branch) => (
            <Card key={branch.id} className="hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex gap-6">
                  <div className="hidden sm:block w-24 h-32 rounded-lg bg-muted overflow-hidden shrink-0">
                    <img
                      src={branch.coverImage || "/placeholder.svg"}
                      alt={branch.title}
                      className="w-full h-full object-cover"
                    />
                  </div>

                  <div className="flex-1 min-w-0 space-y-3">
                    <div>
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        <Badge variant="outline" className="gap-1">
                          <GitBranch className="h-3 w-3" />
                          브랜치
                        </Badge>
                        {branch.mergeStatus === "candidate" && (
                          <Badge variant="default" className="gap-1">
                            <Star className="h-3 w-3" />
                            정사 편입 후보
                          </Badge>
                        )}
                        {branch.mergeStatus === "reviewing" && <Badge variant="secondary">검토 중</Badge>}
                        <Badge variant="outline">{branch.status}</Badge>
                      </div>
                      <Link href={`/branch/${branch.id}`}>
                        <h3 className="font-serif text-xl font-bold mb-1 hover:text-primary transition-colors">
                          {branch.title}
                        </h3>
                      </Link>
                      <p className="text-sm text-muted-foreground mb-2">
                        원작:{" "}
                        <Link href={`/novel/${branch.originalNovelId}`} className="hover:text-primary">
                          {branch.originalNovel}
                        </Link>{" "}
                        | {branch.forkPoint}화에서 분기
                      </p>
                    </div>

                    <p className="text-sm leading-relaxed line-clamp-2">{branch.description}</p>

                    <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                      <Link href={`/author/${branch.authorId}`} className="hover:text-primary">
                        작가: {branch.author}
                      </Link>
                      <span className="flex items-center gap-1">
                        <TrendingUp className="h-3 w-3" />
                        {branch.votes.toLocaleString()} 추천
                      </span>
                      <span className="flex items-center gap-1">
                        <Eye className="h-3 w-3" />
                        {branch.views.toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {branch.chapters}화
                      </span>
                      <span>{branch.lastUpdate}</span>
                    </div>

                    <div className="flex gap-2">
                      <Button size="sm" asChild>
                        <Link href={`/branch/${branch.id}/read/1`}>읽기</Link>
                      </Button>
                      <Button size="sm" variant="outline">
                        <TrendingUp className="mr-2 h-3 w-3" />
                        추천
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </TabsContent>

        {/* Merged Branches */}
        <TabsContent value="merged" className="space-y-4">
          <Card className="bg-gradient-to-br from-primary/5 to-background border-primary/20 mb-6">
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <Star className="h-6 w-6 text-primary shrink-0" />
                <div>
                  <h3 className="font-semibold mb-1">정사 편입이란?</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    독자가 만든 브랜치가 일정 추천 수를 달성하고 원작자의 승인을 받으면, 정사의 외전으로 편입됩니다.
                    원작자는 저작권 매절 계약을 통해 팬 작가에게 보상을 제공합니다.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {mergedBranches.map((branch) => (
            <Card key={branch.id} className="border-primary/20">
              <CardContent className="p-6">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className="gap-1">
                        <Star className="h-3 w-3" />
                        {branch.status}
                      </Badge>
                      <Badge variant="outline">{branch.mergedAt}</Badge>
                    </div>
                    <Link href={`/branch/${branch.id}`}>
                      <h3 className="font-serif text-xl font-bold hover:text-primary transition-colors">
                        {branch.title}
                      </h3>
                    </Link>
                    <p className="text-sm text-muted-foreground">
                      원작: {branch.originalNovel} | {branch.mergedChapter}화에 편입됨
                    </p>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>작가: {branch.author}</span>
                      <span className="flex items-center gap-1">
                        <TrendingUp className="h-3 w-3" />
                        {branch.votes.toLocaleString()} 추천
                      </span>
                    </div>
                  </div>
                  <Button size="sm" asChild>
                    <Link href={`/branch/${branch.id}/read/1`}>
                      읽기
                      <ChevronRight className="ml-2 h-3 w-3" />
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* Trending */}
        <TabsContent value="trending">
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...branches]
              .sort((a, b) => b.votes - a.votes)
              .map((branch, index) => (
                <Card key={branch.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-2 mb-3">
                      <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                        <span className="font-bold text-primary">#{index + 1}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <Link href={`/branch/${branch.id}`}>
                          <h3 className="font-semibold text-sm line-clamp-2 hover:text-primary transition-colors">
                            {branch.title}
                          </h3>
                        </Link>
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground mb-3">원작: {branch.originalNovel}</p>
                    <div className="flex items-center justify-between text-xs">
                      <span className="flex items-center gap-1 text-accent">
                        <TrendingUp className="h-3 w-3" />
                        {branch.votes.toLocaleString()}
                      </span>
                      <span className="text-muted-foreground">{branch.chapters}화</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* CTA */}
      <Card className="mt-12 bg-gradient-to-br from-accent/10 to-background border-accent/20">
        <CardContent className="p-8 text-center">
          <GitBranch className="h-12 w-12 text-accent mx-auto mb-4" />
          <h3 className="font-serif text-2xl font-bold mb-2">나만의 브랜치를 만들어보세요</h3>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            좋아하는 작품의 IF 스토리를 작성하고, 독자들의 추천을 받아 정사에 편입될 기회를 얻으세요
          </p>
          <Button size="lg" asChild>
            <Link href="/novels">
              <GitBranch className="mr-2 h-4 w-4" />
              작품 선택하고 브랜치 만들기
            </Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

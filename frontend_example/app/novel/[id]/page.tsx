import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { BookOpen, Eye, Heart, GitBranch, Star, Share2, Bookmark, ChevronRight } from "lucide-react"
import Link from "next/link"

export default function NovelDetailPage({ params }: { params: { id: string } }) {
  // Mock data
  const novel = {
    id: params.id,
    title: "흑마법사의 회귀",
    author: "마법작가",
    authorId: "author123",
    genre: "판타지",
    tags: ["회귀", "흑마법", "성장", "복수", "먼치킨"],
    description:
      "세계를 멸망시킬 뻔한 마왕을 쓰러뜨린 흑마법사 에스테반. 그러나 그를 기다린 것은 영웅으로서의 영광이 아닌 마녀사냥이었다. 배신당하고 처형당하는 순간, 그는 20년 전 마법학교 입학 시절로 돌아간다. 이번에는 세계를 구하지 않는다. 자신을 배신한 자들에게 복수하고, 진정한 힘을 손에 넣을 것이다.",
    image: "/dark-fantasy-wizard.jpg",
    views: 125430,
    likes: 2340,
    bookmarks: 1820,
    rating: 4.8,
    ratingCount: 892,
    chapters: 245,
    status: "연재중",
    lastUpdate: "2시간 전",
    branches: 23,
  }

  const recentChapters = [
    { chapter: 245, title: "어둠의 심연에서", date: "2시간 전", views: 1234, isNew: true },
    { chapter: 244, title: "금지된 주문", date: "1일 전", views: 3456 },
    { chapter: 243, title: "마탑의 비밀", date: "2일 전", views: 4123 },
    { chapter: 242, title: "과거의 적", date: "3일 전", views: 3890 },
    { chapter: 241, title: "선택의 순간", date: "4일 전", views: 4567 },
  ]

  const topBranches = [
    {
      id: 1,
      title: "IF: 백마법을 선택했다면",
      author: "팬작가A",
      chapters: 15,
      votes: 1234,
      description: "에스테반이 백마법을 선택했다면 어떤 이야기가 펼쳐질까?",
    },
    {
      id: 2,
      title: "IF: 회귀하지 않았다면",
      author: "팬작가B",
      chapters: 23,
      votes: 892,
      description: "과거로 돌아가지 않고 현재에서 복수를 시작한다면?",
    },
  ]

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1">
        {/* Novel Header */}
        <section className="bg-gradient-to-b from-primary/5 to-background py-8">
          <div className="container mx-auto px-4">
            <div className="grid md:grid-cols-[280px_1fr] gap-8">
              {/* Cover Image */}
              <div className="mx-auto md:mx-0">
                <div className="aspect-[3/4] w-full max-w-[280px] rounded-lg overflow-hidden shadow-lg">
                  <img
                    src={novel.image || "/placeholder.svg"}
                    alt={novel.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>

              {/* Novel Info */}
              <div className="space-y-6">
                <div className="space-y-3">
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary">{novel.genre}</Badge>
                    <Badge variant="outline">{novel.status}</Badge>
                  </div>
                  <h1 className="font-serif text-3xl md:text-4xl font-bold">{novel.title}</h1>
                  <div className="flex items-center gap-4 text-muted-foreground">
                    <Link href={`/author/${novel.authorId}`} className="hover:text-primary transition-colors">
                      작가: {novel.author}
                    </Link>
                    <span>•</span>
                    <span>최근 업데이트: {novel.lastUpdate}</span>
                  </div>
                </div>

                {/* Stats */}
                <div className="flex flex-wrap gap-6 text-sm">
                  <div className="flex items-center gap-2">
                    <Eye className="h-4 w-4 text-muted-foreground" />
                    <span>
                      조회 <strong className="text-foreground">{novel.views.toLocaleString()}</strong>
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Heart className="h-4 w-4 text-muted-foreground" />
                    <span>
                      좋아요 <strong className="text-foreground">{novel.likes.toLocaleString()}</strong>
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Bookmark className="h-4 w-4 text-muted-foreground" />
                    <span>
                      책갈피 <strong className="text-foreground">{novel.bookmarks.toLocaleString()}</strong>
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Star className="h-4 w-4 text-muted-foreground" />
                    <span>
                      평점 <strong className="text-foreground">{novel.rating}</strong>
                      <span className="text-muted-foreground ml-1">({novel.ratingCount})</span>
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <GitBranch className="h-4 w-4 text-muted-foreground" />
                    <span>
                      브랜치 <strong className="text-foreground">{novel.branches}</strong>
                    </span>
                  </div>
                </div>

                {/* Description */}
                <p className="text-muted-foreground leading-relaxed">{novel.description}</p>

                {/* Tags */}
                <div className="flex flex-wrap gap-2">
                  {novel.tags.map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      #{tag}
                    </Badge>
                  ))}
                </div>

                {/* Actions */}
                <div className="flex flex-wrap gap-3">
                  <Button size="lg" asChild>
                    <Link href={`/novel/${novel.id}/read/1`}>
                      <BookOpen className="mr-2 h-4 w-4" />첫 화부터 읽기
                    </Link>
                  </Button>
                  <Button size="lg" variant="outline">
                    <Heart className="mr-2 h-4 w-4" />
                    좋아요
                  </Button>
                  <Button size="lg" variant="outline">
                    <Bookmark className="mr-2 h-4 w-4" />
                    책갈피
                  </Button>
                  <Button size="lg" variant="outline">
                    <Share2 className="mr-2 h-4 w-4" />
                    공유
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Content Tabs */}
        <section className="py-8">
          <div className="container mx-auto px-4">
            <div className="grid lg:grid-cols-[1fr_320px] gap-8">
              {/* Main Content */}
              <div className="space-y-6">
                {/* Recent Chapters */}
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="font-serif text-2xl font-bold">최근 회차</h2>
                      <Link href={`/novel/${novel.id}/chapters`} className="text-sm text-primary hover:underline">
                        전체보기
                      </Link>
                    </div>
                    <div className="space-y-1">
                      {recentChapters.map((chapter) => (
                        <Link
                          key={chapter.chapter}
                          href={`/novel/${novel.id}/read/${chapter.chapter}`}
                          className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors group"
                        >
                          <div className="flex items-center gap-3 flex-1 min-w-0">
                            <span className="text-sm font-medium text-muted-foreground shrink-0">
                              {chapter.chapter}화
                            </span>
                            <span className="font-medium truncate group-hover:text-primary transition-colors">
                              {chapter.title}
                            </span>
                            {chapter.isNew && (
                              <Badge variant="destructive" className="text-xs shrink-0">
                                NEW
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground shrink-0 ml-4">
                            <span className="hidden sm:inline">{chapter.date}</span>
                            <span className="flex items-center gap-1">
                              <Eye className="h-3 w-3" />
                              {chapter.views.toLocaleString()}
                            </span>
                            <ChevronRight className="h-4 w-4" />
                          </div>
                        </Link>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Branches */}
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="font-serif text-2xl font-bold flex items-center gap-2">
                        <GitBranch className="h-6 w-6 text-accent" />
                        인기 브랜치
                      </h2>
                      <Link
                        href={`/novel/${novel.id}/branches`}
                        className="text-sm text-primary hover:underline flex items-center gap-1"
                      >
                        전체보기
                        <ChevronRight className="h-3 w-3" />
                      </Link>
                    </div>
                    <div className="space-y-4">
                      {topBranches.map((branch) => (
                        <Link
                          key={branch.id}
                          href={`/branch/${branch.id}`}
                          className="block p-4 rounded-lg border border-border hover:border-accent hover:bg-accent/5 transition-all group"
                        >
                          <div className="flex items-start justify-between gap-3 mb-2">
                            <h3 className="font-semibold group-hover:text-accent transition-colors">{branch.title}</h3>
                            <Badge variant="outline" className="shrink-0">
                              {branch.votes} 추천
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">{branch.description}</p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <span>작가: {branch.author}</span>
                            <span>•</span>
                            <span>{branch.chapters}화</span>
                          </div>
                        </Link>
                      ))}
                    </div>
                    <Button variant="outline" className="w-full mt-4 bg-transparent" asChild>
                      <Link href={`/novel/${novel.id}/create-branch`}>
                        <GitBranch className="mr-2 h-4 w-4" />내 브랜치 만들기
                      </Link>
                    </Button>
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
                      <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                        <span className="font-semibold text-primary">마</span>
                      </div>
                      <div>
                        <Link href={`/author/${novel.authorId}`} className="font-medium hover:text-primary">
                          {novel.author}
                        </Link>
                        <p className="text-xs text-muted-foreground">연재 작품 3개</p>
                      </div>
                    </div>
                    <Button variant="outline" className="w-full bg-transparent">
                      작가 팔로우
                    </Button>
                  </CardContent>
                </Card>

                {/* Quick Actions */}
                <Card>
                  <CardContent className="p-6">
                    <h3 className="font-semibold mb-4">빠른 이동</h3>
                    <div className="space-y-2">
                      <Button variant="ghost" className="w-full justify-start" asChild>
                        <Link href={`/novel/${novel.id}/wiki`}>
                          <BookOpen className="mr-2 h-4 w-4" />
                          세계관 위키
                        </Link>
                      </Button>
                      <Button variant="ghost" className="w-full justify-start" asChild>
                        <Link href={`/novel/${novel.id}/map`}>
                          <span className="mr-2">🗺️</span>
                          세계 지도
                        </Link>
                      </Button>
                      <Button variant="ghost" className="w-full justify-start" asChild>
                        <Link href={`/novel/${novel.id}/comments`}>
                          <span className="mr-2">💬</span>
                          댓글 게시판
                        </Link>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}

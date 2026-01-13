import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { BookOpen, GitBranch, Map, Sparkles, TrendingUp, Clock, Eye, Heart } from "lucide-react"
import Link from "next/link"

export default function HomePage() {
  // Mock data
  const featuredNovels = [
    {
      id: 1,
      title: "흑마법사의 회귀",
      author: "작가명",
      genre: "판타지",
      description: "세계를 구한 흑마법사가 다시 과거로 돌아간다.",
      image: "/dark-fantasy-wizard.jpg",
      views: "125K",
      likes: "2.3K",
      chapters: 245,
      status: "연재중",
    },
    {
      id: 2,
      title: "제국의 검",
      author: "작가명",
      genre: "무협",
      description: "황제 직속 암살자가 되어 제국을 지킨다.",
      image: "/medieval-sword-warrior.jpg",
      views: "98K",
      likes: "1.8K",
      chapters: 189,
      status: "연재중",
    },
    {
      id: 3,
      title: "별을 삼킨 마왕",
      author: "작가명",
      genre: "판타지",
      description: "마왕으로 환생한 그는 별들을 삼키기 시작했다.",
      image: "/demon-king-stars.jpg",
      views: "156K",
      likes: "3.1K",
      chapters: 312,
      status: "연재중",
    },
    {
      id: 4,
      title: "시간을 거스르는 자",
      author: "작가명",
      genre: "SF",
      description: "시간여행자가 된 그는 역사를 바꾸기로 결심한다.",
      image: "/time-traveler-sci-fi.jpg",
      views: "87K",
      likes: "1.5K",
      chapters: 167,
      status: "연재중",
    },
  ]

  const trendingBranches = [
    {
      id: 1,
      title: "IF: 흑마법사가 백마법을 배웠다면",
      originalNovel: "흑마법사의 회귀",
      author: "팬작가A",
      votes: 1234,
      chapters: 15,
    },
    {
      id: 2,
      title: "IF: 검이 아닌 마법을 선택했다면",
      originalNovel: "제국의 검",
      author: "팬작가B",
      votes: 892,
      chapters: 23,
    },
    {
      id: 3,
      title: "IF: 마왕이 인간 편이 되었다면",
      originalNovel: "별을 삼킨 마왕",
      author: "팬작가C",
      votes: 756,
      chapters: 12,
    },
  ]

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative bg-gradient-to-b from-primary/5 to-background py-20 md:py-32">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto text-center space-y-6">
              <h1 className="font-serif text-4xl md:text-6xl font-bold text-balance leading-tight">
                당신의 상상이
                <br />
                <span className="text-primary">새로운 세계</span>가 됩니다
              </h1>
              <p className="text-lg md:text-xl text-muted-foreground text-pretty max-w-2xl mx-auto leading-relaxed">
                문맥 인식 위키와 깃 브랜치 기반 팬픽 시스템으로 작가와 독자가 함께 만들어가는 인터랙티브 월드 웹소설
                플랫폼
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
                <Button size="lg" asChild className="text-base">
                  <Link href="/novels">작품 둘러보기</Link>
                </Button>
                <Button size="lg" variant="outline" asChild className="text-base bg-transparent">
                  <Link href="/studio">작가로 시작하기</Link>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16 md:py-24 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="font-serif text-3xl md:text-4xl font-bold mb-4">ForkLore만의 특별한 기능</h2>
              <p className="text-muted-foreground text-lg">독자와 작가 모두를 위한 혁신적인 시스템</p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="text-center">
                <CardHeader>
                  <div className="mx-auto mb-4 h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                    <BookOpen className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-lg">문맥 인식 위키</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    독자가 읽는 회차에 맞춰 스포일러 없이 세계관 정보를 제공합니다
                  </p>
                </CardContent>
              </Card>

              <Card className="text-center">
                <CardHeader>
                  <div className="mx-auto mb-4 h-12 w-12 rounded-lg bg-accent/10 flex items-center justify-center">
                    <GitBranch className="h-6 w-6 text-accent" />
                  </div>
                  <CardTitle className="text-lg">브랜치 시스템</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    깃의 브랜치처럼 IF 스토리를 작성하고 정사에 편입할 수 있습니다
                  </p>
                </CardContent>
              </Card>

              <Card className="text-center">
                <CardHeader>
                  <div className="mx-auto mb-4 h-12 w-12 rounded-lg bg-chart-2/10 flex items-center justify-center">
                    <Map className="h-6 w-6 text-chart-2" />
                  </div>
                  <CardTitle className="text-lg">다이내믹 지도</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    스토리 진행에 따라 변화하는 인터랙티브 세계 지도
                  </p>
                </CardContent>
              </Card>

              <Card className="text-center">
                <CardHeader>
                  <div className="mx-auto mb-4 h-12 w-12 rounded-lg bg-chart-4/10 flex items-center justify-center">
                    <Sparkles className="h-6 w-6 text-chart-4" />
                  </div>
                  <CardTitle className="text-lg">AI 코파일럿</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    작가의 세계관 관리와 위키 생성을 AI가 자동으로 지원합니다
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Featured Novels */}
        <section className="py-16 md:py-24">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="font-serif text-3xl font-bold mb-2">인기 작품</h2>
                <p className="text-muted-foreground">지금 가장 핫한 웹소설</p>
              </div>
              <Button variant="outline" asChild>
                <Link href="/novels">전체보기</Link>
              </Button>
            </div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {featuredNovels.map((novel) => (
                <Card key={novel.id} className="group cursor-pointer overflow-hidden hover:shadow-lg transition-all">
                  <div className="aspect-[3/4] overflow-hidden bg-muted">
                    <img
                      src={novel.image || "/placeholder.svg"}
                      alt={novel.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                  <CardContent className="p-4 space-y-3">
                    <div className="space-y-1">
                      <Badge variant="secondary" className="text-xs">
                        {novel.genre}
                      </Badge>
                      <h3 className="font-serif font-semibold text-lg line-clamp-1">{novel.title}</h3>
                      <p className="text-sm text-muted-foreground">{novel.author}</p>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">{novel.description}</p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground pt-2">
                      <span className="flex items-center gap-1">
                        <Eye className="h-3 w-3" />
                        {novel.views}
                      </span>
                      <span className="flex items-center gap-1">
                        <Heart className="h-3 w-3" />
                        {novel.likes}
                      </span>
                      <span className="flex items-center gap-1">
                        <BookOpen className="h-3 w-3" />
                        {novel.chapters}화
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Trending Branches */}
        <section className="py-16 md:py-24 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="font-serif text-3xl font-bold mb-2 flex items-center gap-2">
                  <GitBranch className="h-8 w-8 text-accent" />
                  인기 브랜치
                </h2>
                <p className="text-muted-foreground">독자들이 만든 IF 스토리</p>
              </div>
              <Button variant="outline" asChild>
                <Link href="/branches">전체보기</Link>
              </Button>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {trendingBranches.map((branch) => (
                <Card key={branch.id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <Badge variant="outline" className="text-xs">
                        <GitBranch className="h-3 w-3 mr-1" />
                        브랜치
                      </Badge>
                      <div className="flex items-center gap-1 text-sm text-accent">
                        <TrendingUp className="h-4 w-4" />
                        {branch.votes}
                      </div>
                    </div>
                    <CardTitle className="text-lg leading-tight">{branch.title}</CardTitle>
                    <p className="text-sm text-muted-foreground">원작: {branch.originalNovel}</p>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">작가: {branch.author}</span>
                      <span className="text-muted-foreground flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {branch.chapters}화
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 md:py-24">
          <div className="container mx-auto px-4">
            <Card className="bg-gradient-to-br from-primary/10 via-accent/5 to-background border-primary/20">
              <CardContent className="p-12 text-center space-y-6">
                <h2 className="font-serif text-3xl md:text-4xl font-bold">지금 바로 시작하세요</h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                  독자로서 인터랙티브한 독서 경험을 즐기거나, 작가로서 AI의 도움을 받아 완벽한 세계관을 구축하세요
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
                  <Button size="lg" asChild>
                    <Link href="/signup">회원가입</Link>
                  </Button>
                  <Button size="lg" variant="outline" asChild>
                    <Link href="/guide">이용 가이드 보기</Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}

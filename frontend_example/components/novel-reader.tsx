"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TooltipProvider } from "@/components/ui/tooltip"
import {
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Settings,
  List,
  MessageSquare,
  Bookmark,
  Heart,
  Home,
  Map,
  X,
} from "lucide-react"
import { Slider } from "@/components/ui/slider"

interface NovelReaderProps {
  novelId: string
  chapter: number
}

export function NovelReader({ novelId, chapter }: NovelReaderProps) {
  const [fontSize, setFontSize] = useState(18)
  const [lineHeight, setLineHeight] = useState(1.8)
  const [showSettings, setShowSettings] = useState(false)
  const [showWikiPanel, setShowWikiPanel] = useState(false)
  const [selectedTerm, setSelectedTerm] = useState<string | null>(null)

  // Mock data
  const novel = {
    id: novelId,
    title: "흑마법사의 회귀",
    author: "마법작가",
    totalChapters: 245,
  }

  const chapterData = {
    chapter: chapter,
    title: "어둠의 심연에서",
    content: `마탑의 최상층, 에스테반은 창밖을 내다보며 과거를 회상했다.

"결국 이 순간이 왔군."

20년 전, 그가 처음 <span class="wiki-term" data-term="아카데미아">아카데미아</span>에 입학했을 때를 떠올렸다. 그때는 세상이 얼마나 잔인한지 몰랐다. 마법에 대한 순수한 열정만으로 가득했던 젊은 날들.

하지만 이제는 다르다. 그는 알고 있었다. <span class="wiki-term" data-term="흑마법">흑마법</span>의 진정한 힘을. 그리고 그것을 두려워하는 자들의 위선을.

"이번엔 다를 거야."

<span class="wiki-term" data-term="에스테반">에스테반</span>의 손끝에서 어둠의 마력이 소용돌이쳤다. 전생에서는 세계를 구하기 위해 금지된 마법을 사용했다가 마녀사냥의 대상이 되었지만, 이번 생에서는 다른 선택을 할 것이다.

창밖으로 <span class="wiki-term" data-term="칼데론 왕국">칼데론 왕국</span>의 수도가 내려다보였다. 저 아래 어딘가에 자신을 배신할 자들이 평화롭게 살고 있을 것이다. 아직은.

"시작하자."

그의 눈빛이 깊은 보라빛으로 빛났다. 회귀자만이 가진 지식과 <span class="wiki-term" data-term="금단의 마법서">금단의 마법서</span>의 힘. 이 두 가지면 충분했다.

첫 번째 표적은 정해져 있었다. 바로 자신을 마녀사냥의 주동자로 만든 <span class="wiki-term" data-term="대신관 발터">대신관 발터</span>. 그는 곧 자신이 저지른 죄의 대가를 치르게 될 것이다.

에스테반은 책상 위의 낡은 일기장을 펼쳤다. 전생의 기억들이 가득 담긴, 아무도 모르는 미래의 기록. 그는 펜을 들어 새로운 장을 시작했다.

"복수의 서막이 오른다."`,
    publishDate: "2시간 전",
    views: 1234,
    likes: 89,
    comments: 45,
  }

  const wikiTerms = {
    아카데미아: {
      title: "아카데미아",
      summary: "칼데론 왕국 최고의 마법학교. 전 대륙에서 재능있는 마법사들이 모여든다.",
      fullDescription:
        "아카데미아는 200년 전 대마법사 메를린에 의해 설립되었다. 현재까지 공개된 정보로는, 에스테반이 수석으로 입학한 것으로 알려져 있다.",
      appearsIn: [1, 5, 12, 34, 67],
    },
    흑마법: {
      title: "흑마법",
      summary: "금지된 마법의 한 분류. 생명력을 대가로 강력한 힘을 얻는다.",
      fullDescription:
        "흑마법은 신성 마법과 반대되는 개념으로, 어둠의 힘을 다룬다. 에스테반은 전생에서 마왕을 물리치기 위해 흑마법을 익혔다.",
      appearsIn: [1, 3, 8, 15, 23],
    },
    에스테반: {
      title: "에스테반 (주인공)",
      summary: "흑마법사. 회귀자. 전생에서 세계를 구했으나 마녀사냥으로 죽임을 당했다.",
      fullDescription:
        "본작의 주인공. 20년 전 아카데미아 입학 시절로 회귀했다. 전생의 기억과 지식을 바탕으로 복수를 계획하고 있다.",
      appearsIn: [1, 2, 3, 4, 5],
    },
    "칼데론 왕국": {
      title: "칼데론 왕국",
      summary: "대륙 중앙에 위치한 강대국. 아카데미아가 위치한 곳이다.",
      fullDescription: "인구 500만의 마법 강국. 현재 왕은 레오폴드 3세. 수도는 칼데론시티.",
      appearsIn: [1, 6, 11, 19, 27],
    },
    "금단의 마법서": {
      title: "금단의 마법서",
      summary: "전설의 흑마법서. 읽는 자에게 막강한 힘을 주지만 대가를 요구한다.",
      fullDescription:
        "에스테반이 마탑 지하에서 발견한 고대의 마법서. 현재 회차에서는 아직 그 진정한 힘이 드러나지 않았다.",
      appearsIn: [1, 4, 9, 18],
    },
    "대신관 발터": {
      title: "대신관 발터",
      summary: "신성교 최고위 성직자. 에스테반을 마녀사냥한 주동자.",
      fullDescription:
        "겉으로는 선량한 성직자지만, 실제로는 권력욕에 가득 찬 인물. 전생에서 에스테반을 처형하는 데 앞장섰다.",
      appearsIn: [1, 15, 34],
    },
  }

  const handleTermClick = (term: string) => {
    setSelectedTerm(term)
    setShowWikiPanel(true)
  }

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-background">
        {/* Reader Header */}
        <header className="sticky top-0 z-40 w-full border-b border-border bg-background/95 backdrop-blur">
          <div className="container mx-auto px-4">
            <div className="flex h-14 items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" asChild>
                  <Link href={`/novel/${novelId}`}>
                    <Home className="h-5 w-5" />
                  </Link>
                </Button>
                <div className="hidden md:flex flex-col">
                  <Link href={`/novel/${novelId}`} className="text-sm font-medium hover:text-primary">
                    {novel.title}
                  </Link>
                  <span className="text-xs text-muted-foreground">
                    {chapter}화 - {chapterData.title}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" onClick={() => setShowWikiPanel(!showWikiPanel)}>
                  <BookOpen className="h-5 w-5" />
                </Button>
                <Button variant="ghost" size="icon" asChild>
                  <Link href={`/novel/${novelId}/map`}>
                    <Map className="h-5 w-5" />
                  </Link>
                </Button>
                <Button variant="ghost" size="icon" asChild>
                  <Link href={`/novel/${novelId}/chapters`}>
                    <List className="h-5 w-5" />
                  </Link>
                </Button>
                <Button variant="ghost" size="icon" onClick={() => setShowSettings(!showSettings)}>
                  <Settings className="h-5 w-5" />
                </Button>
              </div>
            </div>
          </div>
        </header>

        <div className="flex">
          {/* Main Content */}
          <main className="flex-1">
            <div className="container mx-auto px-4 py-8 max-w-4xl">
              {/* Chapter Header */}
              <div className="mb-8 pb-8 border-b border-border">
                <div className="flex items-center gap-2 mb-3">
                  <Badge variant="secondary">제 {chapter} 화</Badge>
                  <span className="text-sm text-muted-foreground">{chapterData.publishDate}</span>
                </div>
                <h1 className="font-serif text-3xl md:text-4xl font-bold mb-4">{chapterData.title}</h1>
                <div className="flex items-center gap-6 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <MessageSquare className="h-4 w-4" />
                    댓글 {chapterData.comments}
                  </span>
                  <span className="flex items-center gap-1">
                    <Heart className="h-4 w-4" />
                    {chapterData.likes}
                  </span>
                </div>
              </div>

              {/* Chapter Content */}
              <article
                className="prose prose-lg max-w-none mb-12"
                style={{
                  fontSize: `${fontSize}px`,
                  lineHeight: lineHeight,
                }}
              >
                <div
                  className="font-serif text-foreground leading-relaxed space-y-6"
                  dangerouslySetInnerHTML={{ __html: chapterData.content }}
                  onClick={(e) => {
                    const target = e.target as HTMLElement
                    if (target.classList.contains("wiki-term")) {
                      const term = target.dataset.term
                      if (term) handleTermClick(term)
                    }
                  }}
                />
              </article>

              {/* Chapter Actions */}
              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <Button variant="outline" className="flex-1 bg-transparent" asChild>
                  <Link href={`/novel/${novelId}/read/${chapter - 1}`}>
                    <ChevronLeft className="mr-2 h-4 w-4" />
                    이전 화
                  </Link>
                </Button>
                <Button variant="outline" className="flex-1 bg-transparent">
                  <Bookmark className="mr-2 h-4 w-4" />
                  책갈피
                </Button>
                <Button variant="outline" className="flex-1 bg-transparent">
                  <Heart className="mr-2 h-4 w-4" />
                  좋아요
                </Button>
                <Button className="flex-1" asChild>
                  <Link href={`/novel/${novelId}/read/${chapter + 1}`}>
                    다음 화
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>

              {/* Comments Section Preview */}
              <Card className="p-6">
                <h3 className="font-semibold text-lg mb-4">댓글 {chapterData.comments}개</h3>
                <div className="space-y-4 mb-4">
                  <div className="p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-medium text-sm">독자123</span>
                      <span className="text-xs text-muted-foreground">1시간 전</span>
                    </div>
                    <p className="text-sm">에스테반의 복수가 시작되는군요! 다음 화가 너무 기대됩니다!</p>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-medium text-sm">판타지러버</span>
                      <span className="text-xs text-muted-foreground">2시간 전</span>
                    </div>
                    <p className="text-sm">흑마법 설정이 정말 좋아요. 세계관이 탄탄해서 몰입이 잘 돼요.</p>
                  </div>
                </div>
                <Button variant="outline" className="w-full bg-transparent">
                  댓글 전체보기
                </Button>
              </Card>
            </div>
          </main>

          {/* Settings Panel */}
          {showSettings && (
            <aside className="fixed right-0 top-14 h-[calc(100vh-3.5rem)] w-80 border-l border-border bg-background p-6 z-30 overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-semibold">뷰어 설정</h3>
                <Button variant="ghost" size="icon" onClick={() => setShowSettings(false)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="text-sm font-medium mb-3 block">글자 크기</label>
                  <Slider
                    value={[fontSize]}
                    onValueChange={(value) => setFontSize(value[0])}
                    min={14}
                    max={24}
                    step={1}
                    className="mb-2"
                  />
                  <div className="text-xs text-muted-foreground text-center">{fontSize}px</div>
                </div>

                <div>
                  <label className="text-sm font-medium mb-3 block">줄 간격</label>
                  <Slider
                    value={[lineHeight]}
                    onValueChange={(value) => setLineHeight(value[0])}
                    min={1.4}
                    max={2.2}
                    step={0.1}
                    className="mb-2"
                  />
                  <div className="text-xs text-muted-foreground text-center">{lineHeight.toFixed(1)}</div>
                </div>
              </div>
            </aside>
          )}

          {/* Wiki Panel */}
          {showWikiPanel && (
            <aside className="fixed right-0 top-14 h-[calc(100vh-3.5rem)] w-80 border-l border-border bg-background p-6 z-30 overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-semibold flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-primary" />
                  세계관 위키
                </h3>
                <Button variant="ghost" size="icon" onClick={() => setShowWikiPanel(false)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {selectedTerm && wikiTerms[selectedTerm as keyof typeof wikiTerms] ? (
                <div className="space-y-4">
                  <div>
                    <h4 className="font-serif text-xl font-bold mb-2">
                      {wikiTerms[selectedTerm as keyof typeof wikiTerms].title}
                    </h4>
                    <Badge variant="secondary" className="mb-4">
                      {chapter}화까지 공개
                    </Badge>
                    <p className="text-sm text-muted-foreground leading-relaxed mb-4">
                      {wikiTerms[selectedTerm as keyof typeof wikiTerms].fullDescription}
                    </p>
                  </div>

                  <div>
                    <h5 className="text-sm font-semibold mb-2">등장 회차</h5>
                    <div className="flex flex-wrap gap-2">
                      {wikiTerms[selectedTerm as keyof typeof wikiTerms].appearsIn.map((ch) => (
                        <Link key={ch} href={`/novel/${novelId}/read/${ch}`}>
                          <Badge
                            variant="outline"
                            className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
                          >
                            {ch}화
                          </Badge>
                        </Link>
                      ))}
                    </div>
                  </div>

                  <Button variant="outline" className="w-full bg-transparent" asChild>
                    <Link href={`/novel/${novelId}/wiki/${selectedTerm}`}>위키 전체보기</Link>
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-sm text-muted-foreground mb-4">
                    본문의 밑줄 친 용어를 클릭하면 스포일러 없이 세계관 정보를 확인할 수 있습니다.
                  </p>
                  <div className="space-y-2">
                    {Object.keys(wikiTerms).map((term) => (
                      <Button
                        key={term}
                        variant="ghost"
                        className="w-full justify-start"
                        onClick={() => handleTermClick(term)}
                      >
                        {term}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </aside>
          )}
        </div>

        <style jsx global>{`
          .wiki-term {
            color: rgb(var(--color-primary));
            text-decoration: underline;
            text-decoration-style: dotted;
            cursor: pointer;
            transition: all 0.2s;
          }
          .wiki-term:hover {
            text-decoration-style: solid;
            font-weight: 500;
          }
        `}</style>
      </div>
    </TooltipProvider>
  )
}

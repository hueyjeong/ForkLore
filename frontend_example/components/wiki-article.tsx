"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BookOpen, Clock, Edit, History, MessageSquare, Share2, ChevronLeft, AlertCircle } from "lucide-react"
import { Slider } from "@/components/ui/slider"

interface WikiArticleProps {
  novelId: string
  term: string
}

export function WikiArticle({ novelId, term }: WikiArticleProps) {
  const [currentChapter, setCurrentChapter] = useState(245)

  // Mock data
  const article = {
    title: "에스테반",
    type: "등장인물",
    role: "주인공",
    status: "생존",
    firstAppearance: 1,
    imageUrl: "/placeholder.svg?height=400&width=400",

    // 회차별로 누적되는 정보
    snapshots: [
      {
        validFrom: 1,
        validUntil: 15,
        content: {
          summary: "아카데미아에 입학한 신입생. 흑마법에 관심이 많다.",
          fullDescription:
            "에스테반은 평범한 배경을 가진 마법학교 신입생이다. 다른 학생들과 달리 흑마법에 깊은 관심을 보이며, 금지된 서적들을 몰래 읽는 모습이 목격된다.",
          relationships: ["리디아 (동기)", "교수 카를 (스승)"],
          abilities: ["기초 마법", "마력 감지"],
        },
      },
      {
        validFrom: 16,
        validUntil: 50,
        content: {
          summary: "흑마법을 익히기 시작한 학생. 숨겨진 재능이 드러난다.",
          fullDescription:
            "에스테반의 진짜 정체가 서서히 드러난다. 그는 단순한 학생이 아니라, 과거에서 온 회귀자였다. 전생의 기억을 바탕으로 빠르게 성장하며, 금지된 마탑에서 '금단의 마법서'를 발견한다.",
          relationships: ["리디아 (연인 관계 발전)", "대신관 발터 (적대 관계)", "교수 카를 (스승)"],
          abilities: ["기초 마법", "마력 감지", "흑마법 입문", "시간 마법 감지"],
        },
      },
      {
        validFrom: 51,
        validUntil: 245,
        content: {
          summary: "회귀자. 전생에서 세계를 구한 영웅이었으나 배신당해 죽었다. 복수를 계획 중.",
          fullDescription:
            "에스테반의 전생 이야기가 완전히 밝혀진다. 그는 50년 후의 미래에서 마왕을 쓰러뜨린 영웅이었지만, 흑마법을 사용했다는 이유로 마녀사냥의 대상이 되어 처형당했다. '시간의 펜던트'의 힘으로 20년 전 아카데미아 입학 시절로 돌아온 그는, 이번 생에서는 세계를 구하지 않고 자신을 배신한 자들에게 복수하기로 결심한다.",
          relationships: [
            "리디아 (전생의 연인, 현생에서 재회)",
            "대신관 발터 (복수 대상 1순위)",
            "황제 레온하르트 (전생에서 배신자)",
            "마왕 아자젤 (전생에서 쓰러뜨림)",
          ],
          abilities: ["고급 흑마법", "금단의 주문들", "시간 마법", "영혼 조작", "차원 이동", "전생의 기억과 지식"],
        },
      },
    ],

    timeline: [
      { chapter: 1, event: "아카데미아 입학", description: "평범한 신입생으로 입학" },
      { chapter: 15, event: "리디아와의 만남", description: "운명적인 재회" },
      { chapter: 34, event: "금단의 마법서 발견", description: "금지된 마탑 지하에서 발견" },
      { chapter: 67, event: "회귀자 정체 드러남", description: "독자들에게 처음 공개됨" },
      { chapter: 123, event: "첫 번째 복수 시작", description: "대신관 발터를 표적으로 삼음" },
      { chapter: 189, event: "과거의 진실", description: "전생의 배신 사건 회상" },
      { chapter: 234, event: "금단의 마법서 완성", description: "모든 주문을 마스터함" },
    ],

    relatedArticles: [
      { name: "리디아", type: "등장인물", relation: "연인" },
      { name: "대신관 발터", type: "등장인물", relation: "적대자" },
      { name: "금단의 마법서", type: "아이템", relation: "소유" },
      { name: "시간의 펜던트", type: "아이템", relation: "소유" },
      { name: "흑마법", type: "개념", relation: "전문 분야" },
      { name: "회귀", type: "개념", relation: "핵심 설정" },
    ],

    history: [
      { version: "v3", date: "234화", editor: "작가님 (AI 보조)", change: "금단의 마법서 마스터 추가" },
      { version: "v2", date: "123화", editor: "작가님 (AI 보조)", change: "복수 계획 정보 추가" },
      { version: "v1", date: "67화", editor: "작가님", change: "회귀자 정체 공개" },
    ],
  }

  // 현재 회차에 해당하는 스냅샷 찾기
  const getCurrentSnapshot = () => {
    for (let i = article.snapshots.length - 1; i >= 0; i--) {
      if (currentChapter >= article.snapshots[i].validFrom) {
        return article.snapshots[i]
      }
    }
    return article.snapshots[0]
  }

  const currentSnapshot = getCurrentSnapshot()
  const visibleTimeline = article.timeline.filter((event) => event.chapter <= currentChapter)

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-6">
        <Link href={`/novel/${novelId}`} className="text-sm text-muted-foreground hover:text-primary">
          흑마법사의 회귀
        </Link>
        <span className="text-muted-foreground">/</span>
        <Link href={`/novel/${novelId}/wiki`} className="text-sm text-muted-foreground hover:text-primary">
          위키
        </Link>
        <span className="text-muted-foreground">/</span>
        <span className="text-sm font-medium">{term}</span>
      </div>

      {/* Context Control */}
      <Card className="mb-8 bg-primary/5 border-primary/20">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-primary shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold mb-1">문맥 인식 모드</h3>
              <p className="text-sm text-muted-foreground mb-3">
                현재 {currentChapter}화 기준 정보를 표시합니다. 슬라이더를 조절하여 다른 시점의 정보를 확인할 수
                있습니다.
              </p>
              <div className="space-y-2">
                <Slider
                  value={[currentChapter]}
                  onValueChange={(value) => setCurrentChapter(value[0])}
                  min={1}
                  max={245}
                  step={1}
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>1화</span>
                  <span className="font-medium text-foreground">{currentChapter}화</span>
                  <span>245화</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid lg:grid-cols-[1fr_300px] gap-8">
        {/* Main Content */}
        <div className="space-y-6">
          {/* Article Header */}
          <Card>
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row gap-6">
                <div className="w-full md:w-48 h-48 rounded-lg bg-muted overflow-hidden shrink-0">
                  <img
                    src={article.imageUrl || "/placeholder.svg"}
                    alt={article.title}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex-1 space-y-4">
                  <div>
                    <div className="flex flex-wrap gap-2 mb-3">
                      <Badge variant="secondary">{article.type}</Badge>
                      <Badge variant="outline">{article.role}</Badge>
                      <Badge variant={article.status === "생존" ? "outline" : "secondary"}>{article.status}</Badge>
                    </div>
                    <h1 className="font-serif text-3xl font-bold mb-2">{article.title}</h1>
                    <p className="text-muted-foreground">{currentSnapshot.content.summary}</p>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    <span>첫 등장: {article.firstAppearance}화</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button variant="outline" size="sm">
                      <Share2 className="mr-2 h-3 w-3" />
                      공유
                    </Button>
                    <Button variant="outline" size="sm">
                      <MessageSquare className="mr-2 h-3 w-3" />
                      토론
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Article Tabs */}
          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList>
              <TabsTrigger value="overview">개요</TabsTrigger>
              <TabsTrigger value="timeline">타임라인</TabsTrigger>
              <TabsTrigger value="history">편집 기록</TabsTrigger>
            </TabsList>

            {/* Overview */}
            <TabsContent value="overview" className="space-y-6">
              <Card>
                <CardContent className="p-6 prose prose-sm max-w-none">
                  <h3 className="font-serif text-xl font-bold mb-3">상세 설명</h3>
                  <p className="text-muted-foreground leading-relaxed">{currentSnapshot.content.fullDescription}</p>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <h3 className="font-serif text-xl font-bold mb-4">능력</h3>
                  <div className="flex flex-wrap gap-2">
                    {currentSnapshot.content.abilities.map((ability, index) => (
                      <Badge key={index} variant="outline">
                        {ability}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <h3 className="font-serif text-xl font-bold mb-4">관계</h3>
                  <div className="space-y-2">
                    {currentSnapshot.content.relationships.map((relationship, index) => (
                      <div key={index} className="flex items-center gap-2 text-sm">
                        <div className="h-2 w-2 rounded-full bg-primary" />
                        <span>{relationship}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Timeline */}
            <TabsContent value="timeline">
              <Card>
                <CardContent className="p-6">
                  <h3 className="font-serif text-xl font-bold mb-6">주요 사건</h3>
                  <div className="space-y-4">
                    {visibleTimeline.map((event, index) => (
                      <div key={index} className="flex gap-4">
                        <div className="flex flex-col items-center">
                          <div className="h-3 w-3 rounded-full bg-primary shrink-0" />
                          {index < visibleTimeline.length - 1 && <div className="w-0.5 h-full bg-border mt-1" />}
                        </div>
                        <div className="flex-1 pb-6">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant="outline" className="text-xs">
                              {event.chapter}화
                            </Badge>
                            <h4 className="font-semibold">{event.event}</h4>
                          </div>
                          <p className="text-sm text-muted-foreground">{event.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* History */}
            <TabsContent value="history">
              <Card>
                <CardContent className="p-6">
                  <h3 className="font-serif text-xl font-bold mb-4 flex items-center gap-2">
                    <History className="h-5 w-5" />
                    편집 기록
                  </h3>
                  <div className="space-y-3">
                    {article.history.map((record, index) => (
                      <div key={index} className="p-3 rounded-lg border border-border">
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">
                              {record.version}
                            </Badge>
                            <span className="text-sm font-medium">{record.editor}</span>
                          </div>
                          <span className="text-xs text-muted-foreground">{record.date}</span>
                        </div>
                        <p className="text-sm text-muted-foreground">{record.change}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Related Articles */}
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-4">관련 항목</h3>
              <div className="space-y-2">
                {article.relatedArticles.map((related, index) => (
                  <Link
                    key={index}
                    href={`/novel/${novelId}/wiki/${related.name}`}
                    className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50 transition-colors group"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate group-hover:text-primary">{related.name}</div>
                      <div className="text-xs text-muted-foreground">{related.relation}</div>
                    </div>
                    <Badge variant="outline" className="text-xs shrink-0 ml-2">
                      {related.type}
                    </Badge>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-4">바로가기</h3>
              <div className="space-y-2">
                <Button variant="ghost" className="w-full justify-start" asChild>
                  <Link href={`/novel/${novelId}/read/${article.firstAppearance}`}>
                    <BookOpen className="mr-2 h-4 w-4" />첫 등장 회차 보기
                  </Link>
                </Button>
                <Button variant="ghost" className="w-full justify-start" asChild>
                  <Link href={`/novel/${novelId}/map`}>
                    <span className="mr-2">🗺️</span>지도에서 보기
                  </Link>
                </Button>
                <Button variant="ghost" className="w-full justify-start">
                  <Edit className="mr-2 h-4 w-4" />
                  수정 제안하기
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Back Button */}
      <div className="mt-8">
        <Button variant="outline" asChild>
          <Link href={`/novel/${novelId}/wiki`}>
            <ChevronLeft className="mr-2 h-4 w-4" />
            위키 목록으로
          </Link>
        </Button>
      </div>
    </div>
  )
}

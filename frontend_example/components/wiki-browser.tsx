"use client"

import { useState } from "react"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Search, BookOpen, Users, MapIcon, Sparkles, Clock, AlertCircle } from "lucide-react"
import { Slider } from "@/components/ui/slider"

interface WikiBrowserProps {
  novelId: string
}

export function WikiBrowser({ novelId }: WikiBrowserProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [currentChapter, setCurrentChapter] = useState(245)

  // Mock data - 문맥 인식 위키 데이터
  const wikiData = {
    characters: [
      {
        id: "esteban",
        name: "에스테반",
        role: "주인공",
        summary: "흑마법사. 회귀자. 복수를 계획 중.",
        firstAppearance: 1,
        lastUpdate: 245,
        status: "생존",
        imageUrl: "/placeholder.svg?height=100&width=100",
      },
      {
        id: "walter",
        name: "대신관 발터",
        role: "적대자",
        summary: "신성교 최고위 성직자. 에스테반의 첫 번째 복수 대상.",
        firstAppearance: 15,
        lastUpdate: 234,
        status: "생존",
        imageUrl: "/placeholder.svg?height=100&width=100",
      },
      {
        id: "lydia",
        name: "리디아",
        role: "조력자",
        summary: "아카데미아 동기. 전생에서는 에스테반의 연인이었다.",
        firstAppearance: 5,
        lastUpdate: 243,
        status: "생존",
        imageUrl: "/placeholder.svg?height=100&width=100",
      },
    ],
    locations: [
      {
        id: "academia",
        name: "아카데미아",
        type: "교육기관",
        summary: "칼데론 왕국 최고의 마법학교",
        firstAppearance: 1,
        lastUpdate: 245,
        imageUrl: "/placeholder.svg?height=100&width=100",
      },
      {
        id: "calderon",
        name: "칼데론 왕국",
        type: "국가",
        summary: "대륙 중앙의 강대국. 인구 500만.",
        firstAppearance: 1,
        lastUpdate: 241,
        imageUrl: "/placeholder.svg?height=100&width=100",
      },
      {
        id: "tower",
        name: "금지된 마탑",
        type: "던전",
        summary: "고대 흑마법사들의 비밀 연구소",
        firstAppearance: 34,
        lastUpdate: 189,
        imageUrl: "/placeholder.svg?height=100&width=100",
      },
    ],
    items: [
      {
        id: "grimoire",
        name: "금단의 마법서",
        type: "마법 아이템",
        summary: "전설의 흑마법서. 막강한 힘과 함께 대가를 요구한다.",
        firstAppearance: 4,
        lastUpdate: 234,
        rarity: "전설",
        imageUrl: "/placeholder.svg?height=100&width=100",
      },
      {
        id: "pendant",
        name: "시간의 펜던트",
        type: "유물",
        summary: "회귀의 원인으로 추정되는 신비한 펜던트",
        firstAppearance: 1,
        lastUpdate: 156,
        rarity: "유일",
        imageUrl: "/placeholder.svg?height=100&width=100",
      },
    ],
    concepts: [
      {
        id: "dark-magic",
        name: "흑마법",
        type: "마법 체계",
        summary: "금지된 마법. 생명력을 대가로 강력한 힘을 얻는다.",
        firstAppearance: 1,
        lastUpdate: 245,
      },
      {
        id: "regression",
        name: "회귀",
        type: "현상",
        summary: "과거로 돌아가는 현상. 에스테반이 경험한 핵심 사건.",
        firstAppearance: 1,
        lastUpdate: 178,
      },
    ],
  }

  const novel = {
    title: "흑마법사의 회귀",
    totalChapters: 245,
  }

  // 현재 회차까지 공개된 항목만 필터링
  const filterByChapter = (items: any[]) => {
    return items.filter((item) => item.firstAppearance <= currentChapter)
  }

  const filteredCharacters = filterByChapter(wikiData.characters)
  const filteredLocations = filterByChapter(wikiData.locations)
  const filteredItems = filterByChapter(wikiData.items)
  const filteredConcepts = filterByChapter(wikiData.concepts)

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Link href={`/novel/${novelId}`} className="text-sm text-muted-foreground hover:text-primary">
            {novel.title}
          </Link>
          <span className="text-muted-foreground">/</span>
          <span className="text-sm font-medium">세계관 위키</span>
        </div>
        <h1 className="font-serif text-3xl md:text-4xl font-bold mb-4">세계관 위키</h1>
        <p className="text-muted-foreground max-w-2xl leading-relaxed">
          독자가 읽은 회차까지의 정보만 표시됩니다. 스포일러 걱정 없이 세계관을 탐험하세요.
        </p>
      </div>

      {/* Context Control */}
      <Card className="mb-8 bg-primary/5 border-primary/20">
        <CardContent className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <AlertCircle className="h-5 w-5 text-primary" />
            <div>
              <h3 className="font-semibold">문맥 인식 모드</h3>
              <p className="text-sm text-muted-foreground">현재 {currentChapter}화까지 읽은 것으로 설정됨</p>
            </div>
          </div>
          <div className="space-y-3">
            <Slider
              value={[currentChapter]}
              onValueChange={(value) => setCurrentChapter(value[0])}
              min={1}
              max={novel.totalChapters}
              step={1}
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>1화</span>
              <span>{currentChapter}화</span>
              <span>{novel.totalChapters}화</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Search */}
      <div className="relative mb-8">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="search"
          placeholder="등장인물, 장소, 아이템 검색..."
          className="pl-9"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Wiki Content */}
      <Tabs defaultValue="characters" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 lg:w-auto lg:inline-grid">
          <TabsTrigger value="characters" className="gap-2">
            <Users className="h-4 w-4" />
            <span className="hidden sm:inline">등장인물</span>
          </TabsTrigger>
          <TabsTrigger value="locations" className="gap-2">
            <MapIcon className="h-4 w-4" />
            <span className="hidden sm:inline">장소</span>
          </TabsTrigger>
          <TabsTrigger value="items" className="gap-2">
            <Sparkles className="h-4 w-4" />
            <span className="hidden sm:inline">아이템</span>
          </TabsTrigger>
          <TabsTrigger value="concepts" className="gap-2">
            <BookOpen className="h-4 w-4" />
            <span className="hidden sm:inline">개념</span>
          </TabsTrigger>
        </TabsList>

        {/* Characters Tab */}
        <TabsContent value="characters">
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredCharacters.map((character) => (
              <Link key={character.id} href={`/novel/${novelId}/wiki/${character.name}`}>
                <Card className="h-full hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-4">
                    <div className="flex gap-3 mb-3">
                      <div className="h-16 w-16 rounded-lg bg-muted overflow-hidden shrink-0">
                        <img
                          src={character.imageUrl || "/placeholder.svg"}
                          alt={character.name}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-lg mb-1 truncate">{character.name}</h3>
                        <Badge variant="secondary" className="text-xs">
                          {character.role}
                        </Badge>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed mb-3">
                      {character.summary}
                    </p>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />첫 등장: {character.firstAppearance}화
                      </span>
                      <Badge variant={character.status === "생존" ? "outline" : "secondary"} className="text-xs">
                        {character.status}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </TabsContent>

        {/* Locations Tab */}
        <TabsContent value="locations">
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredLocations.map((location) => (
              <Link key={location.id} href={`/novel/${novelId}/wiki/${location.name}`}>
                <Card className="h-full hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-4">
                    <div className="aspect-video rounded-lg bg-muted overflow-hidden mb-3">
                      <img
                        src={location.imageUrl || "/placeholder.svg"}
                        alt={location.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="space-y-2">
                      <div>
                        <h3 className="font-semibold text-lg">{location.name}</h3>
                        <Badge variant="secondary" className="text-xs mt-1">
                          {location.type}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">{location.summary}</p>
                      <div className="text-xs text-muted-foreground flex items-center gap-1">
                        <Clock className="h-3 w-3" />첫 등장: {location.firstAppearance}화
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </TabsContent>

        {/* Items Tab */}
        <TabsContent value="items">
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredItems.map((item) => (
              <Link key={item.id} href={`/novel/${novelId}/wiki/${item.name}`}>
                <Card className="h-full hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-4">
                    <div className="flex gap-3 mb-3">
                      <div className="h-16 w-16 rounded-lg bg-muted overflow-hidden shrink-0">
                        <img
                          src={item.imageUrl || "/placeholder.svg"}
                          alt={item.name}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-lg mb-1 truncate">{item.name}</h3>
                        <Badge variant={item.rarity === "전설" ? "default" : "secondary"} className="text-xs">
                          {item.rarity}
                        </Badge>
                      </div>
                    </div>
                    <Badge variant="outline" className="text-xs mb-2">
                      {item.type}
                    </Badge>
                    <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed mb-3">{item.summary}</p>
                    <div className="text-xs text-muted-foreground flex items-center gap-1">
                      <Clock className="h-3 w-3" />첫 등장: {item.firstAppearance}화
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </TabsContent>

        {/* Concepts Tab */}
        <TabsContent value="concepts">
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredConcepts.map((concept) => (
              <Link key={concept.id} href={`/novel/${novelId}/wiki/${concept.name}`}>
                <Card className="h-full hover:shadow-md transition-shadow cursor-pointer">
                  <CardHeader>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        <BookOpen className="h-5 w-5 text-primary" />
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {concept.type}
                      </Badge>
                    </div>
                    <CardTitle className="text-lg">{concept.name}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground line-clamp-3 leading-relaxed mb-3">{concept.summary}</p>
                    <div className="text-xs text-muted-foreground flex items-center gap-1">
                      <Clock className="h-3 w-3" />첫 등장: {concept.firstAppearance}화
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* AI Assistant CTA */}
      <Card className="mt-12 bg-gradient-to-br from-accent/10 to-background border-accent/20">
        <CardContent className="p-8 text-center">
          <Sparkles className="h-12 w-12 text-accent mx-auto mb-4" />
          <h3 className="font-serif text-2xl font-bold mb-2">세계관에 대해 궁금한 점이 있나요?</h3>
          <p className="text-muted-foreground mb-6">AI가 현재 회차까지의 정보를 바탕으로 질문에 답변해드립니다</p>
          <Button size="lg">
            <Sparkles className="mr-2 h-4 w-4" />
            AI에게 질문하기
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

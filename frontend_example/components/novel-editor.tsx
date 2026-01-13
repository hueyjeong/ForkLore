"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Save,
  Eye,
  Send,
  ChevronLeft,
  Settings,
  Sparkles,
  BookOpen,
  Calendar,
  Wand2,
  CheckCircle2,
  XCircle,
} from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface NovelEditorProps {
  novelId: string
  chapterId?: string
}

export function NovelEditor({ novelId, chapterId }: NovelEditorProps) {
  const [title, setTitle] = useState("어둠의 심연에서")
  const [content, setContent] = useState(`마탑의 최상층, 에스테반은 창밖을 내다보며 과거를 회상했다.

"결국 이 순간이 왔군."

20년 전, 그가 처음 아카데미아에 입학했을 때를 떠올렸다. 그때는 세상이 얼마나 잔인한지 몰랐다. 마법에 대한 순수한 열정만으로 가득했던 젊은 날들.

하지만 이제는 다르다. 그는 알고 있었다. 흑마법의 진정한 힘을. 그리고 그것을 두려워하는 자들의 위선을.

"이번엔 다를 거야."

에스테반의 손끝에서 어둠의 마력이 소용돌이쳤다.`)

  const [showAIPanel, setShowAIPanel] = useState(false)
  const [aiSuggestions, setAiSuggestions] = useState({
    wikiEntries: [
      { term: "아카데미아", status: "new", confidence: 0.95 },
      { term: "흑마법", status: "update", confidence: 0.88 },
      { term: "에스테반", status: "update", confidence: 0.92 },
    ],
    consistencyChecks: [
      { type: "success", message: "캐릭터 성격 일관성 확인됨" },
      { type: "warning", message: "이전 회차에서 '마력의 색깔'이 붉은색으로 묘사되었습니다" },
    ],
  })

  const novel = {
    title: "흑마법사의 회귀",
    currentChapter: 245,
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Editor Header */}
      <header className="sticky top-0 z-40 w-full border-b border-border bg-background/95 backdrop-blur">
        <div className="container mx-auto px-4">
          <div className="flex h-14 items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="icon" asChild>
                <Link href="/studio">
                  <ChevronLeft className="h-5 w-5" />
                </Link>
              </Button>
              <div className="hidden md:block">
                <div className="text-sm font-medium">{novel.title}</div>
                <div className="text-xs text-muted-foreground">{novel.currentChapter}화 작성 중</div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm">
                <Eye className="mr-2 h-4 w-4" />
                미리보기
              </Button>
              <Button variant="outline" size="sm">
                <Save className="mr-2 h-4 w-4" />
                임시저장
              </Button>
              <Button size="sm">
                <Send className="mr-2 h-4 w-4" />
                발행
              </Button>
              <Button variant="ghost" size="icon" onClick={() => setShowAIPanel(!showAIPanel)}>
                <Sparkles className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Main Editor */}
        <main className="flex-1">
          <div className="container mx-auto px-4 py-8 max-w-4xl">
            {/* Chapter Info */}
            <div className="mb-6 space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">회차 번호</label>
                <div className="flex items-center gap-4">
                  <Badge variant="secondary" className="text-lg px-4 py-2">
                    제 {novel.currentChapter} 화
                  </Badge>
                  <Button variant="outline" size="sm">
                    <Calendar className="mr-2 h-3 w-3" />
                    예약 발행
                  </Button>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">제목</label>
                <Input
                  type="text"
                  placeholder="회차 제목을 입력하세요"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="text-lg font-serif"
                />
              </div>
            </div>

            {/* Content Editor */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium">본문</label>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">{content.length.toLocaleString()} 자</span>
                  <Button variant="ghost" size="sm" className="h-7 text-xs">
                    <Wand2 className="mr-1 h-3 w-3" />
                    AI 문장 다듬기
                  </Button>
                </div>
              </div>
              <Card>
                <CardContent className="p-0">
                  <Textarea
                    placeholder="이야기를 작성하세요..."
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    className="min-h-[600px] font-serif text-base leading-relaxed border-0 focus-visible:ring-0 resize-none"
                  />
                </CardContent>
              </Card>
              <p className="text-xs text-muted-foreground mt-2">
                마크다운 문법을 사용할 수 있습니다. **굵게**, *기울임*, [위키용어]로 위키 링크를 추가하세요.
              </p>
            </div>

            {/* Editor Tips */}
            <Card className="bg-muted/30">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <BookOpen className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                  <div className="text-sm space-y-1">
                    <p className="font-medium">에디터 팁</p>
                    <ul className="text-muted-foreground space-y-1 list-disc list-inside">
                      <li>위키 항목은 [용어명]으로 표시하면 자동으로 링크됩니다</li>
                      <li>AI가 새로운 설정을 감지하면 자동으로 위키 초안을 생성합니다</li>
                      <li>이전 회차와 일관성을 유지하려면 AI 제안을 확인하세요</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>

        {/* AI Panel */}
        {showAIPanel && (
          <aside className="w-80 border-l border-border bg-background overflow-y-auto">
            <div className="p-6 space-y-6">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-accent" />
                    AI 코파일럿
                  </h3>
                  <Button variant="ghost" size="sm" onClick={() => setShowAIPanel(false)}>
                    닫기
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">AI가 작성 중인 내용을 분석하고 도움을 제공합니다</p>
              </div>

              <Tabs defaultValue="wiki" className="space-y-4">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="wiki" className="text-xs">
                    위키 제안
                  </TabsTrigger>
                  <TabsTrigger value="check" className="text-xs">
                    일관성 검사
                  </TabsTrigger>
                </TabsList>

                {/* Wiki Suggestions */}
                <TabsContent value="wiki" className="space-y-3">
                  <div>
                    <h4 className="text-sm font-medium mb-3">발견된 위키 항목</h4>
                    <div className="space-y-2">
                      {aiSuggestions.wikiEntries.map((entry, index) => (
                        <Card key={index} className="p-3">
                          <div className="flex items-start justify-between gap-2 mb-2">
                            <div className="flex-1">
                              <div className="font-medium text-sm">{entry.term}</div>
                              <Badge
                                variant={entry.status === "new" ? "default" : "secondary"}
                                className="text-xs mt-1"
                              >
                                {entry.status === "new" ? "신규 항목" : "업데이트"}
                              </Badge>
                            </div>
                            <div className="text-xs text-muted-foreground">{Math.round(entry.confidence * 100)}%</div>
                          </div>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline" className="flex-1 h-7 text-xs bg-transparent">
                              승인
                            </Button>
                            <Button size="sm" variant="ghost" className="flex-1 h-7 text-xs">
                              무시
                            </Button>
                          </div>
                        </Card>
                      ))}
                    </div>
                  </div>

                  <Button variant="outline" className="w-full bg-transparent" size="sm">
                    <Wand2 className="mr-2 h-3 w-3" />
                    위키 자동 생성
                  </Button>
                </TabsContent>

                {/* Consistency Check */}
                <TabsContent value="check" className="space-y-3">
                  <div>
                    <h4 className="text-sm font-medium mb-3">세계관 일관성</h4>
                    <div className="space-y-2">
                      {aiSuggestions.consistencyChecks.map((check, index) => (
                        <div
                          key={index}
                          className={`p-3 rounded-lg border ${
                            check.type === "success"
                              ? "border-green-500/20 bg-green-500/5"
                              : "border-yellow-500/20 bg-yellow-500/5"
                          }`}
                        >
                          <div className="flex items-start gap-2">
                            {check.type === "success" ? (
                              <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0 mt-0.5" />
                            ) : (
                              <XCircle className="h-4 w-4 text-yellow-500 shrink-0 mt-0.5" />
                            )}
                            <p className="text-xs leading-relaxed">{check.message}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <Button variant="outline" className="w-full bg-transparent" size="sm">
                    <Sparkles className="mr-2 h-3 w-3" />
                    전체 검사 실행
                  </Button>
                </TabsContent>
              </Tabs>

              {/* Quick Actions */}
              <Card className="bg-muted/30">
                <CardContent className="p-4 space-y-2">
                  <h4 className="text-sm font-medium mb-2">빠른 작업</h4>
                  <Button variant="ghost" size="sm" className="w-full justify-start h-8 text-xs">
                    <Wand2 className="mr-2 h-3 w-3" />
                    문장 개선 제안
                  </Button>
                  <Button variant="ghost" size="sm" className="w-full justify-start h-8 text-xs">
                    <BookOpen className="mr-2 h-3 w-3" />
                    이전 회차 참조
                  </Button>
                  <Button variant="ghost" size="sm" className="w-full justify-start h-8 text-xs">
                    <Settings className="mr-2 h-3 w-3" />
                    AI 설정
                  </Button>
                </CardContent>
              </Card>
            </div>
          </aside>
        )}
      </div>
    </div>
  )
}

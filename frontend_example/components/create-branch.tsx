"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"
import { GitBranch, ChevronLeft, Info } from "lucide-react"

interface CreateBranchProps {
  novelId: string
}

export function CreateBranch({ novelId }: CreateBranchProps) {
  const [selectedChapter, setSelectedChapter] = useState(5)
  const [branchTitle, setBranchTitle] = useState("")
  const [branchDescription, setBranchDescription] = useState("")

  // Mock data
  const novel = {
    id: novelId,
    title: "흑마법사의 회귀",
    totalChapters: 245,
    coverImage: "/dark-fantasy-wizard.jpg",
  }

  const chapters = [
    { chapter: 5, title: "첫 번째 선택", description: "에스테반이 흑마법과 백마법 중 하나를 선택하는 순간" },
    { chapter: 15, title: "리디아와의 만남", description: "운명적인 만남의 순간" },
    { chapter: 34, title: "금단의 마법서 발견", description: "금지된 마탑 지하에서의 선택" },
    { chapter: 67, title: "회귀자 정체 드러남", description: "진실을 밝히는 순간" },
  ]

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-6">
        <Link href={`/novel/${novelId}`} className="text-sm text-muted-foreground hover:text-primary">
          {novel.title}
        </Link>
        <span className="text-muted-foreground">/</span>
        <span className="text-sm font-medium">브랜치 만들기</span>
      </div>

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <GitBranch className="h-8 w-8 text-accent" />
          <h1 className="font-serif text-3xl font-bold">브랜치 만들기</h1>
        </div>
        <p className="text-muted-foreground leading-relaxed">
          원작의 특정 시점에서 분기하여 나만의 IF 스토리를 만들어보세요.
        </p>
      </div>

      {/* Info Card */}
      <Card className="mb-8 bg-accent/5 border-accent/20">
        <CardContent className="p-6">
          <div className="flex items-start gap-3">
            <Info className="h-5 w-5 text-accent shrink-0 mt-0.5" />
            <div className="space-y-2 text-sm">
              <h3 className="font-semibold">브랜치 시스템이란?</h3>
              <ul className="text-muted-foreground space-y-1 list-disc list-inside leading-relaxed">
                <li>원작의 특정 회차에서 분기하여 다른 전개의 스토리를 작성할 수 있습니다</li>
                <li>분기 시점까지의 설정, 위키, 지도 정보를 모두 상속받습니다</li>
                <li>일정 추천 수를 달성하면 정사 편입 후보가 되어 원작자의 검토를 받습니다</li>
                <li>정사에 편입되면 저작권 매절 계약을 통해 보상을 받습니다</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Original Novel */}
      <Card className="mb-8">
        <CardContent className="p-6">
          <h2 className="font-serif text-xl font-bold mb-4">원작 작품</h2>
          <div className="flex gap-4">
            <div className="w-20 h-28 rounded-lg bg-muted overflow-hidden shrink-0">
              <img
                src={novel.coverImage || "/placeholder.svg"}
                alt={novel.title}
                className="w-full h-full object-cover"
              />
            </div>
            <div>
              <h3 className="font-serif font-semibold text-lg mb-1">{novel.title}</h3>
              <p className="text-sm text-muted-foreground">총 {novel.totalChapters}화 연재 중</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Select Fork Point */}
      <Card className="mb-8">
        <CardContent className="p-6">
          <h2 className="font-serif text-xl font-bold mb-4">분기 지점 선택</h2>
          <p className="text-sm text-muted-foreground mb-4">
            어느 회차에서 이야기를 분기하시겠습니까? 이 시점까지의 모든 설정을 상속받습니다.
          </p>
          <div className="space-y-2">
            {chapters.map((chapter) => (
              <button
                key={chapter.chapter}
                onClick={() => setSelectedChapter(chapter.chapter)}
                className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                  selectedChapter === chapter.chapter
                    ? "border-accent bg-accent/5"
                    : "border-border hover:border-accent/50 hover:bg-muted/50"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant={selectedChapter === chapter.chapter ? "default" : "outline"}>
                        {chapter.chapter}화
                      </Badge>
                      <h4 className="font-semibold">{chapter.title}</h4>
                    </div>
                    <p className="text-sm text-muted-foreground">{chapter.description}</p>
                  </div>
                  {selectedChapter === chapter.chapter && (
                    <div className="h-5 w-5 rounded-full bg-accent flex items-center justify-center shrink-0">
                      <div className="h-2 w-2 rounded-full bg-accent-foreground" />
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Branch Details */}
      <Card className="mb-8">
        <CardContent className="p-6 space-y-6">
          <div>
            <h2 className="font-serif text-xl font-bold mb-4">브랜치 정보</h2>
          </div>

          <div className="space-y-2">
            <Label htmlFor="title">브랜치 제목 *</Label>
            <Input
              id="title"
              type="text"
              placeholder="예: IF: 흑마법사가 백마법을 배웠다면"
              value={branchTitle}
              onChange={(e) => setBranchTitle(e.target.value)}
              className="font-serif"
            />
            <p className="text-xs text-muted-foreground">IF로 시작하는 제목을 추천합니다</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">브랜치 설명 *</Label>
            <Textarea
              id="description"
              placeholder="이 브랜치에서 어떤 이야기가 펼쳐질지 설명해주세요..."
              value={branchDescription}
              onChange={(e) => setBranchDescription(e.target.value)}
              className="min-h-[120px] resize-none"
            />
            <p className="text-xs text-muted-foreground">{branchDescription.length} / 500자</p>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-4">
        <Button variant="outline" asChild className="sm:flex-1 bg-transparent">
          <Link href={`/novel/${novelId}`}>
            <ChevronLeft className="mr-2 h-4 w-4" />
            취소
          </Link>
        </Button>
        <Button
          className="sm:flex-1"
          disabled={!branchTitle || !branchDescription}
          onClick={() => {
            // Handle branch creation
            alert("브랜치가 생성되었습니다!")
          }}
        >
          <GitBranch className="mr-2 h-4 w-4" />
          브랜치 만들고 첫 화 작성하기
        </Button>
      </div>
    </div>
  )
}

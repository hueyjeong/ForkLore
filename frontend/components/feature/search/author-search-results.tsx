'use client'

import { Search } from 'lucide-react'

interface AuthorSearchResultsProps {
  searchQuery: string
}

export function AuthorSearchResults({ searchQuery }: AuthorSearchResultsProps) {
  if (!searchQuery) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
        <div className="p-4 rounded-full bg-muted">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <div className="space-y-2">
          <h3 className="text-xl font-semibold">작가 검색</h3>
          <p className="text-muted-foreground">
            검색어를 입력하면 작가를 찾을 수 있습니다.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center justify-center py-20 text-center space-y-4 border-2 border-dashed rounded-xl bg-muted/30">
      <div className="p-4 rounded-full bg-muted">
        <Search className="h-8 w-8 text-muted-foreground" />
      </div>
      <div className="space-y-2">
        <h3 className="text-xl font-semibold">작가 검색 준비 중</h3>
        <p className="text-muted-foreground">
          작가 검색 기능은 곧 제공될 예정입니다.
        </p>
        <p className="text-sm text-muted-foreground">
          현재는 소설 목록에서 작가 정보를 확인할 수 있습니다.
        </p>
      </div>
    </div>
  )
}

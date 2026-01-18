import { Badge } from "@/components/ui/badge"

interface NovelBadgeProps {
  isPremium?: boolean
  isExclusive?: boolean
}

export function NovelBadge({ isPremium, isExclusive }: NovelBadgeProps) {
  if (!isPremium && !isExclusive) return null

  return (
    <div className="flex gap-1">
      {isPremium && (
        <Badge
          className="bg-[#FFD700] text-white border-transparent hover:bg-[#FFD700]/90"
        >
          PLUS
        </Badge>
      )}
      {isExclusive && (
        <Badge
          className="bg-[#3B82F6] text-white border-transparent hover:bg-[#3B82F6]/90"
        >
          독점
        </Badge>
      )}
    </div>
  )
}

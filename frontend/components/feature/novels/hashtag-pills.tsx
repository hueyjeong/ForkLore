import { Badge } from "@/components/ui/badge"

interface HashtagPillsProps {
  tags: string[]
  maxDisplay?: number
}

export function HashtagPills({ tags, maxDisplay = 8 }: HashtagPillsProps) {
  if (!tags || tags.length === 0) {
    return null
  }

  const displayTags = tags.slice(0, maxDisplay)
  const remainingCount = tags.length - maxDisplay

  return (
    <div className="flex flex-wrap gap-1">
      {displayTags.map((tag) => (
        <Badge key={tag} variant="secondary" className="font-normal">
          #{tag}
        </Badge>
      ))}
      {remainingCount > 0 && (
        <Badge variant="outline" className="font-normal">
          +{remainingCount} more
        </Badge>
      )}
    </div>
  )
}

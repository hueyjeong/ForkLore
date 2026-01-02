import { NovelReader } from "@/components/novel-reader"

export default function ReadChapterPage({ params }: { params: { id: string; chapter: string } }) {
  return <NovelReader novelId={params.id} chapter={Number.parseInt(params.chapter)} />
}

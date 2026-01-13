import { NovelEditor } from "@/components/novel-editor"

export default function WritePage({ params }: { params: { novelId: string } }) {
  return <NovelEditor novelId={params.novelId} />
}

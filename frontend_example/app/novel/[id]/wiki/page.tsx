import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { WikiBrowser } from "@/components/wiki-browser"

export default function NovelWikiPage({ params }: { params: { id: string } }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <WikiBrowser novelId={params.id} />
      </main>
      <Footer />
    </div>
  )
}

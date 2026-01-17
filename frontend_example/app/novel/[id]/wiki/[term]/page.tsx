import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { WikiArticle } from "@/components/wiki-article"

export default function WikiTermPage({ params }: { params: { id: string; term: string } }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <WikiArticle novelId={params.id} term={decodeURIComponent(params.term)} />
      </main>
      <Footer />
    </div>
  )
}

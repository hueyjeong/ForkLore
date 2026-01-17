import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { AuthorDashboard } from "@/components/author-dashboard"

export default function StudioPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <AuthorDashboard />
      </main>
      <Footer />
    </div>
  )
}

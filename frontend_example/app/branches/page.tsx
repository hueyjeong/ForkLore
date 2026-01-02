import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { BranchExplorer } from "@/components/branch-explorer"

export default function BranchesPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <BranchExplorer />
      </main>
      <Footer />
    </div>
  )
}

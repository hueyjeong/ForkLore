import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { BranchDetail } from "@/components/branch-detail"

export default function BranchDetailPage({ params }: { params: { id: string } }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <BranchDetail branchId={params.id} />
      </main>
      <Footer />
    </div>
  )
}

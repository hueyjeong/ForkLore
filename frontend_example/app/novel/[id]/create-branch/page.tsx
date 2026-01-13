import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { CreateBranch } from "@/components/create-branch"

export default function CreateBranchPage({ params }: { params: { id: string } }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <CreateBranch novelId={params.id} />
      </main>
      <Footer />
    </div>
  )
}

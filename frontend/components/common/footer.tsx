import Link from "next/link"

export function Footer() {
  return (
    <footer className="w-full border-t bg-background py-6 md:py-8">
      <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row md:py-0 px-4 md:px-8">
        <div className="flex flex-col items-center gap-4 px-8 md:flex-row md:gap-2 md:px-0">
          <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
            Built by{" "}
            <a
              href="#"
              target="_blank"
              rel="noreferrer"
              className="font-medium underline underline-offset-4"
            >
              ForkLore Team
            </a>
            . The source code is available on{" "}
            <a
              href="https://github.com/forklore/forklore" // Example link
              target="_blank"
              rel="noreferrer"
              className="font-medium underline underline-offset-4"
            >
              GitHub
            </a>
            .
          </p>
        </div>
        <div className="flex gap-4">
          <Link href="/terms" className="text-sm font-medium text-muted-foreground hover:underline">
            Terms
          </Link>
          <Link href="/privacy" className="text-sm font-medium text-muted-foreground hover:underline">
            Privacy
          </Link>
        </div>
      </div>
    </footer>
  )
}

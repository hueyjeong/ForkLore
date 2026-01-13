import Link from "next/link"

export function Footer() {
  return (
    <footer className="w-full border-t bg-muted/30 pt-12 pb-8">
      <div className="container px-4 md:px-8 mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          {/* Brand Col */}
          <div className="col-span-1 md:col-span-1 flex flex-col gap-4">
            <Link href="/" className="group">
              <span className="text-2xl font-bold font-serif text-premium">ForkLore</span>
            </Link>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Where stories fork, legends begin. Experience the multiverse of narratives in a premium reading environment.
            </p>
          </div>

          {/* Links Col 1 */}
          <div>
            <h4 className="font-semibold mb-4">Platform</h4>
            <nav className="flex flex-col gap-2">
              <Link href="/novels" className="text-sm text-muted-foreground hover:text-primary transition-colors">Novels</Link>
              <Link href="/ranking" className="text-sm text-muted-foreground hover:text-primary transition-colors">Ranking</Link>
              <Link href="/community" className="text-sm text-muted-foreground hover:text-primary transition-colors">Community</Link>
            </nav>
          </div>

          {/* Links Col 2 */}
          <div>
            <h4 className="font-semibold mb-4">Support</h4>
            <nav className="flex flex-col gap-2">
              <Link href="/help" className="text-sm text-muted-foreground hover:text-primary transition-colors">Help Center</Link>
              <Link href="/terms" className="text-sm text-muted-foreground hover:text-primary transition-colors">Terms of Service</Link>
              <Link href="/privacy" className="text-sm text-muted-foreground hover:text-primary transition-colors">Privacy Policy</Link>
            </nav>
          </div>

          {/* Social Col */}
          <div>
            <h4 className="font-semibold mb-4">Follow Us</h4>
            <div className="flex gap-4">
              <a href="#" className="h-9 w-9 rounded-full bg-accent/50 flex items-center justify-center hover:bg-primary hover:text-primary-foreground transition-all">
                <span className="sr-only">Twitter</span>
                <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24"><path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.84 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/></svg>
              </a>
              <a href="#" className="h-9 w-9 rounded-full bg-accent/50 flex items-center justify-center hover:bg-primary hover:text-primary-foreground transition-all">
                <span className="sr-only">Discord</span>
                <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24"><path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028 14.09 14.09 0 001.226-1.994.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.078.078 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03z"/></svg>
              </a>
            </div>
          </div>
        </div>

        <div className="pt-8 border-t border-border/20 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-xs text-muted-foreground">
            &copy; {new Date().getFullYear()} ForkLore Team. All rights reserved.
          </p>
          <div className="flex gap-6">
            <Link href="/terms" className="text-xs text-muted-foreground hover:text-primary">Terms</Link>
            <Link href="/privacy" className="text-xs text-muted-foreground hover:text-primary">Privacy</Link>
            <Link href="/cookies" className="text-xs text-muted-foreground hover:text-primary">Cookies</Link>
          </div>
        </div>
      </div>
    </footer>
  )
}

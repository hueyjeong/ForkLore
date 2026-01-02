import Link from "next/link"
import { BookOpen } from "lucide-react"

export function Footer() {
  return (
    <footer className="border-t border-border bg-muted/30">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <Link href="/" className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-primary" />
              <span className="font-serif text-lg font-bold">ForkLore</span>
            </Link>
            <p className="text-sm text-muted-foreground leading-relaxed">인터랙티브 월드 웹소설 플랫폼</p>
          </div>

          {/* 서비스 */}
          <div>
            <h3 className="font-semibold mb-4 text-sm">서비스</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/novels" className="text-muted-foreground hover:text-primary transition-colors">
                  작품 둘러보기
                </Link>
              </li>
              <li>
                <Link href="/ranking" className="text-muted-foreground hover:text-primary transition-colors">
                  랭킹
                </Link>
              </li>
              <li>
                <Link href="/branches" className="text-muted-foreground hover:text-primary transition-colors">
                  브랜치 시스템
                </Link>
              </li>
              <li>
                <Link href="/studio" className="text-muted-foreground hover:text-primary transition-colors">
                  작가 스튜디오
                </Link>
              </li>
            </ul>
          </div>

          {/* 고객지원 */}
          <div>
            <h3 className="font-semibold mb-4 text-sm">고객지원</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/help" className="text-muted-foreground hover:text-primary transition-colors">
                  공지사항
                </Link>
              </li>
              <li>
                <Link href="/faq" className="text-muted-foreground hover:text-primary transition-colors">
                  자주 묻는 질문
                </Link>
              </li>
              <li>
                <Link href="/guide" className="text-muted-foreground hover:text-primary transition-colors">
                  이용 가이드
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-muted-foreground hover:text-primary transition-colors">
                  문의하기
                </Link>
              </li>
            </ul>
          </div>

          {/* 정책 */}
          <div>
            <h3 className="font-semibold mb-4 text-sm">정책</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/terms" className="text-muted-foreground hover:text-primary transition-colors">
                  이용약관
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-muted-foreground hover:text-primary transition-colors">
                  개인정보처리방침
                </Link>
              </li>
              <li>
                <Link href="/youth" className="text-muted-foreground hover:text-primary transition-colors">
                  청소년보호정책
                </Link>
              </li>
              <li>
                <Link href="/copyright" className="text-muted-foreground hover:text-primary transition-colors">
                  저작권 정책
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-border">
          <p className="text-xs text-muted-foreground text-center">
            © 2026 ForkLore. All rights reserved. 인터랙티브 월드 웹소설 플랫폼
          </p>
        </div>
      </div>
    </footer>
  )
}

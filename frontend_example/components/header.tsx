"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Bell, Gift, Menu, Search, User, BookOpen, Moon, Sun } from "lucide-react"
import { useState } from "react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function Header() {
  const [theme, setTheme] = useState<"light" | "dark">("light")

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light"
    setTheme(newTheme)
    document.documentElement.classList.toggle("dark")
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between gap-4">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            <span className="font-serif text-xl font-bold text-foreground">ForkLore</span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <Link href="/novels" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
              작품
            </Link>
            <Link href="/ranking" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
              랭킹
            </Link>
            <Link href="/free" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
              자유연재
            </Link>
            <Link href="/branches" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
              브랜치
            </Link>
            <Link href="/studio" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
              작가스튜디오
            </Link>
          </nav>

          {/* Search */}
          <div className="hidden lg:flex flex-1 max-w-md">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input type="search" placeholder="작품, 작가, 태그 검색..." className="w-full pl-9 bg-muted/50" />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={toggleTheme}>
              {theme === "light" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
            </Button>

            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-accent" />
            </Button>

            <Button variant="ghost" size="icon">
              <Gift className="h-5 w-5" />
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                  <User className="h-5 w-5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem>
                  <User className="mr-2 h-4 w-4" />내 서재
                </DropdownMenuItem>
                <DropdownMenuItem>마일리지: 1,250P</DropdownMenuItem>
                <DropdownMenuItem>코인: 500C</DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem>설정</DropdownMenuItem>
                <DropdownMenuItem>로그아웃</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Button variant="ghost" size="icon" className="md:hidden">
              <Menu className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Search */}
      <div className="lg:hidden border-t border-border px-4 py-2">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input type="search" placeholder="작품, 작가, 태그 검색..." className="w-full pl-9 bg-muted/50" />
        </div>
      </div>
    </header>
  )
}

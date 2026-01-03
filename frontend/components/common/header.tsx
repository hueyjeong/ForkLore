"use client"

import * as React from "react"
import Link from "next/link"
import { Menu, Search, User } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from "@/components/ui/sheet"
import { Separator } from "@/components/ui/separator"
import { ThemeToggle } from "@/components/theme-toggle"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"

export function Header() {
  const [isScrolled, setIsScrolled] = React.useState(false)

  React.useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0)
    }
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  return (
    <header
      className={cn(
        "sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 transition-colors",
        isScrolled ? "shadow-sm" : ""
      )}
    >
      <div className="container flex h-14 items-center gap-4 px-4 md:px-8">
        {/* Mobile Menu (Hamburger) */}
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="md:hidden shrink-0">
              <Menu className="h-5 w-5" />
              <span className="sr-only">Toggle menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-[300px] sm:w-[400px]">
            <SheetTitle className="sr-only">Mobile Menu</SheetTitle> {/* Accessibility Fix */}
            <div className="flex flex-col gap-6 py-6">
              <Link href="/" className="flex items-center gap-2">
                <span className="text-xl font-bold font-serif">ForkLore</span>
              </Link>
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input type="search" placeholder="Search..." className="w-full pl-8" />
              </div>
              <nav className="flex flex-col gap-4">
                <Link href="/novels" className="text-lg font-medium hover:underline">
                  Novels
                </Link>
                <Link href="/ranking" className="text-lg font-medium hover:underline">
                  Ranking
                </Link>
                <Link href="/community" className="text-lg font-medium hover:underline">
                  Community
                </Link>
              </nav>
            </div>
          </SheetContent>
        </Sheet>

        {/* Logo */}
        <Link href="/" className="mr-6 flex items-center gap-2">
          <span className="hidden md:inline-block text-xl font-bold font-serif" role="heading" aria-level={1}>
            ForkLore
          </span>
          <span className="md:hidden text-lg font-bold font-serif">ForkLore</span>
        </Link>
        
        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
          <Link href="/novels" className="transition-colors hover:text-foreground/80 text-foreground/60">
            Novels
          </Link>
          <Link href="/ranking" className="transition-colors hover:text-foreground/80 text-foreground/60">
            Ranking
          </Link>
          <Link href="/community" className="transition-colors hover:text-foreground/80 text-foreground/60">
            Community
          </Link>
        </nav>

        {/* Right Utils */}
        <div className="flex flex-1 items-center justify-end gap-2 md:gap-4">
          <div className="relative hidden md:block w-full max-w-[200px] lg:max-w-[300px]">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search novels..."
              className="h-9 w-full pl-8 bg-muted/50"
            />
          </div>
          
          <ThemeToggle />

          {/* User Menu (Mock) */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src="/avatars/01.png" alt="@user" />
                  <AvatarFallback>
                    <User className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Profile</DropdownMenuItem>
              <DropdownMenuItem>Library</DropdownMenuItem>
              <DropdownMenuItem>Settings</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Log out</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}

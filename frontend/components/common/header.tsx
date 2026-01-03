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
        "sticky top-0 z-50 w-full transition-all duration-300",
        isScrolled 
          ? "glass shadow-sm h-14" 
          : "bg-transparent h-16 border-transparent"
      )}
    >
      <div className="container flex h-full items-center gap-4 px-4 md:px-8 mx-auto">
        {/* Mobile Menu (Hamburger) */}
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="md:hidden shrink-0 hover:bg-accent/50">
              <Menu className="h-5 w-5" />
              <span className="sr-only">Toggle menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="glass w-[300px] sm:w-[400px] border-r border-border/20">
            <SheetTitle className="text-premium text-2xl mb-8">ForkLore</SheetTitle>
            <div className="flex flex-col gap-8 py-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input type="search" placeholder="Search stories..." className="w-full pl-10 bg-muted/30 border-none focus-visible:ring-primary/30" />
              </div>
              <nav className="flex flex-col gap-6">
                <Link href="/novels" className="text-xl font-medium hover:text-primary transition-colors">
                  Novels
                </Link>
                <Link href="/ranking" className="text-xl font-medium hover:text-primary transition-colors">
                  Ranking
                </Link>
                <Link href="/community" className="text-xl font-medium hover:text-primary transition-colors">
                  Community
                </Link>
              </nav>
            </div>
          </SheetContent>
        </Sheet>

        {/* Logo */}
        <Link href="/" className="mr-8 flex items-center gap-2 group">
          <span className="text-2xl font-bold text-premium bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70 group-hover:to-primary transition-all duration-500">
            ForkLore
          </span>
        </Link>
        
        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium">
          <Link href="/novels" className="relative py-1 transition-colors hover:text-primary text-foreground/70 after:absolute after:bottom-0 after:left-0 after:h-0.5 after:w-0 hover:after:w-full after:bg-primary after:transition-all">
            Novels
          </Link>
          <Link href="/ranking" className="relative py-1 transition-colors hover:text-primary text-foreground/70 after:absolute after:bottom-0 after:left-0 after:h-0.5 after:w-0 hover:after:w-full after:bg-primary after:transition-all">
            Ranking
          </Link>
          <Link href="/community" className="relative py-1 transition-colors hover:text-primary text-foreground/70 after:absolute after:bottom-0 after:left-0 after:h-0.5 after:w-0 hover:after:w-full after:bg-primary after:transition-all">
            Community
          </Link>
        </nav>

        {/* Right Utils */}
        <div className="flex flex-1 items-center justify-end gap-2 md:gap-4">
          <div className="relative hidden md:block w-full max-w-[200px] lg:max-w-[280px] group">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground group-focus-within:text-primary transition-colors" />
            <Input
              type="search"
              placeholder="Search novels..."
              className="h-9 w-full pl-10 bg-muted/50 border-transparent focus:bg-muted/80 focus:border-primary/20 transition-all rounded-full"
            />
          </div>
          
          <ThemeToggle />

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="rounded-full hover:bg-accent/50 p-0 overflow-hidden border border-border/50">
                <Avatar className="h-8 w-8">
                  <AvatarImage src="/avatars/01.png" alt="@user" />
                  <AvatarFallback className="bg-primary/10 text-primary">
                    <User className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="glass w-56 p-2 border-border/20">
              <DropdownMenuLabel className="font-premium">My Account</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-border/20" />
              <DropdownMenuItem className="focus:bg-primary/10 focus:text-primary cursor-pointer">Profile</DropdownMenuItem>
              <DropdownMenuItem className="focus:bg-primary/10 focus:text-primary cursor-pointer">Library</DropdownMenuItem>
              <DropdownMenuItem className="focus:bg-primary/10 focus:text-primary cursor-pointer">Settings</DropdownMenuItem>
              <DropdownMenuSeparator className="bg-border/20" />
              <DropdownMenuItem className="text-destructive focus:bg-destructive/10 focus:text-destructive cursor-pointer">Log out</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}

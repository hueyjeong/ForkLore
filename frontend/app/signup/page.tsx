"use client"

import Link from "next/link"
import { cn } from "@/lib/utils"
import { buttonVariants } from "@/components/ui/button"
import { UserSignupForm } from "@/components/auth/user-signup-form"

export default function SignupPage() {
  return (
    <div className="fixed inset-0 min-h-screen flex items-stretch">
      {/* Left Panel: Immersive Decorative */}
      <div className="relative hidden w-1/2 flex-col bg-muted p-12 text-white lg:flex overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center transition-transform duration-1000 hover:scale-105" 
          style={{ backgroundImage: "url('/auth_background_ethereal_library.png')" }}
        />
        <div className="absolute inset-0 bg-black/40 backdrop-blur-[2px]" />
        
        <Link href="/" className="relative z-20 flex items-center text-2xl font-bold font-serif text-premium">
          ForkLore
        </Link>
        
        <div className="relative z-20 mt-auto">
          <blockquote className="space-y-4">
            <p className="text-2xl font-serif italic leading-relaxed">
              "당신만의 전설을 시작하세요.<br />
              무한한 이야기의 세계가 기다립니다."
            </p>
            <footer className="text-sm font-medium opacity-80">Join the Multiverse</footer>
          </blockquote>
        </div>
      </div>

      {/* Right Panel: Clean Auth Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-background relative selection:bg-primary/20">
        <div className="absolute top-8 right-8">
          <Link
            href="/login"
            className={cn(
              buttonVariants({ variant: "ghost" }),
              "text-sm font-medium hover:bg-accent/50"
            )}
          >
            로그인
          </Link>
        </div>

        <div className="mx-auto flex w-full flex-col justify-center space-y-8 sm:w-[400px] py-12">
          <div className="flex flex-col space-y-3 text-center lg:text-left">
            <h1 className="text-3xl font-bold font-serif tracking-tight text-premium">
              Create Account
            </h1>
            <p className="text-sm text-muted-foreground leading-relaxed">
              ForkLore의 일원이 되어 나만의 이야기를 발견하고<br />
              작가들과 소통해보세요.
            </p>
          </div>
          
          <UserSignupForm />
          
          <p className="px-8 text-center text-xs text-muted-foreground leading-relaxed">
            회원가입 시 ForkLore의{" "}
            <Link
              href="/terms"
              className="underline underline-offset-4 hover:text-primary transition-colors"
            >
              이용약관
            </Link>
            과{" "}
            <Link
              href="/privacy"
              className="underline underline-offset-4 hover:text-primary transition-colors"
            >
              개인정보처리방침
            </Link>
            에 동의하게 됩니다.
          </p>
        </div>
      </div>
    </div>
  )
}

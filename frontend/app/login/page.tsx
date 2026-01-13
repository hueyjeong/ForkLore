"use client"

import Link from "next/link"
import { UserLoginForm } from "@/components/auth/user-login-form"

export default function LoginPage() {
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
              &quot;모든 이야기는 갈림길에서 시작되고,<br />
              당신의 선택으로 전설이 완성됩니다.&quot;
            </p>
            <footer className="text-sm font-medium opacity-80">ForkLore Multiverse</footer>
          </blockquote>
        </div>
      </div>

      {/* Right Panel: Clean Auth Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-background relative selection:bg-primary/20">
        <div className="mx-auto flex w-full flex-col justify-center space-y-8 sm:w-[400px]">
          <div className="flex flex-col space-y-3 text-center lg:text-left">
            <h1 className="text-3xl font-bold font-serif tracking-tight text-premium">
              Welcome back
            </h1>
            <p className="text-sm text-muted-foreground leading-relaxed">
              이야기의 다음 장을 써내려갈 준비가 되셨나요?<br />
              이메일로 로그인하여 계속하세요.
            </p>
          </div>
          
          <UserLoginForm />

          <div className="text-center text-sm">
            <span className="text-muted-foreground">계정이 없으신가요? </span>
            <Link
              href="/signup"
              className="font-medium text-primary hover:underline underline-offset-4"
            >
              회원가입
            </Link>
          </div>
          
          <p className="px-8 text-center text-xs text-muted-foreground leading-relaxed">
            로그인 시 ForkLore의{" "}
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

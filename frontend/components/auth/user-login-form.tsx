"use client"

import * as React from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { useRouter } from "next/navigation"
import { toast } from "sonner"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Icons } from "@/components/icons"
import { useAuthStore } from "@/stores/auth-store"

// eslint-disable-next-line @typescript-eslint/no-empty-object-type
interface UserLoginFormProps extends React.HTMLAttributes<HTMLDivElement> {
  // Add specific props if needed
}

const loginSchema = z.object({
  email: z.string().email({ message: "이메일 형식이 올바르지 않습니다." }),
  password: z.string().min(8, { message: "비밀번호는 최소 8자 이상이어야 합니다." }),
})

type FormData = z.infer<typeof loginSchema>

export function UserLoginForm({ className, ...props }: UserLoginFormProps) {
  const router = useRouter()
  const login = useAuthStore((state) => state.login)
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(loginSchema),
  })
  const [isLoading, setIsLoading] = React.useState<boolean>(false)

  async function onSubmit(data: FormData) {
    setIsLoading(true)

    try {
      await login(data)
      toast.success("로그인에 성공했습니다.")
      router.push("/")
    } catch (error: any) {
      let errorMessage = "로그인에 실패했습니다."
      
      if (error.response?.status === 401) {
        errorMessage = "이메일 또는 비밀번호가 일치하지 않습니다."
      } else if (error.message) {
        errorMessage = error.message
      }
      
      toast.error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSocialLogin = (provider: 'google' | 'github') => {
    // TODO: Issue #59 - NextAuth.js v5 소셜 로그인 연동
    // import { signIn } from "next-auth/react"
    // await signIn(provider, { callbackUrl: "/" })
    toast.info(`${provider} 로그인 준비 중...`);
  };

  return (
    <div className={cn("grid gap-6", className)} {...props}>
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="email">이메일</Label>
            <Input
              id="email"
              placeholder="name@example.com"
              type="email"
              autoCapitalize="none"
              autoComplete="email"
              autoCorrect="off"
              disabled={isLoading}
              className="bg-muted/30 border-border/50 focus:border-primary/50 transition-all h-11"
              {...register("email")}
            />
            {errors?.email && (
              <p className="text-xs text-destructive mt-1 font-medium">
                {errors.email.message}
              </p>
            )}
          </div>
          <div className="grid gap-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="password">비밀번호</Label>
              <Button variant="link" className="px-0 font-normal text-xs text-muted-foreground hover:text-primary">
                비밀번호를 잊으셨나요?
              </Button>
            </div>
            <Input
              id="password"
              placeholder="••••••••"
              type="password"
              autoCapitalize="none"
              autoCorrect="off"
              disabled={isLoading}
              className="bg-muted/30 border-border/50 focus:border-primary/50 transition-all h-11"
              {...register("password")}
            />
            {errors?.password && (
              <p className="text-xs text-destructive mt-1 font-medium">
                {errors.password.message}
              </p>
            )}
          </div>
          <Button type="submit" disabled={isLoading} className="h-11 grad-primary hover:opacity-90 transition-opacity text-white font-semibold">
            {isLoading && (
              <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
            )}
            로그인
          </Button>
        </div>
      </form>
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-border/50" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground font-medium tracking-wider">
            또는 소셜 계정으로 로그인
          </span>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <Button variant="outline" type="button" disabled={isLoading} className="h-11 border-border/50 hover:bg-muted/50 transition-all">
          <Icons.google className="mr-2 h-4 w-4" />
          Google
        </Button>
        <Button variant="outline" type="button" disabled={isLoading} className="h-11 border-border/50 hover:bg-muted/50 transition-all">
          <Icons.gitHub className="mr-2 h-4 w-4" />
          GitHub
        </Button>
      </div>
    </div>
  )
}

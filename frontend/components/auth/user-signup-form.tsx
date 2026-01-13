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
interface UserSignupFormProps extends React.HTMLAttributes<HTMLDivElement> {
  // Add specific props if needed
}

const signupSchema = z.object({
  email: z.string().email({ message: "이메일 형식이 올바르지 않습니다." }),
  nickname: z.string().min(2, { message: "닉네임은 최소 2자 이상이어야 합니다." }),
  birthDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, { message: "YYYY-MM-DD 형식을 사용해주세요." }),
  password: z.string().min(8, { message: "비밀번호는 최소 8자 이상이어야 합니다." }),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "비밀번호가 일치하지 않습니다.",
  path: ["confirmPassword"],
})

type FormData = z.infer<typeof signupSchema>

export function UserSignupForm({ className, ...props }: UserSignupFormProps) {
  const router = useRouter()
  const signup = useAuthStore((state) => state.signup)
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(signupSchema),
  })
  const [isLoading, setIsLoading] = React.useState<boolean>(false)

  async function onSubmit(data: FormData) {
    setIsLoading(true)

    try {
      // confirmPassword만 제외하고 나머지 필드는 모두 백엔드로 전송
      const { confirmPassword, ...signupData } = data
      await signup(signupData)
      
      toast.success("회원가입이 완료되었습니다. 로그인해주세요.")
      router.push("/login")
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "회원가입에 실패했습니다."
      toast.error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

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
              disabled={isLoading}
              className="bg-muted/30 border-border/50 focus:border-primary/50 transition-all h-10"
              {...register("email")}
            />
            {errors?.email && (
              <p className="text-xs text-destructive mt-1">{errors.email.message}</p>
            )}
          </div>
          <div className="grid gap-2">
            <Label htmlFor="nickname">닉네임</Label>
            <Input
              id="nickname"
              placeholder="사용할 닉네임"
              type="text"
              disabled={isLoading}
              className="bg-muted/30 border-border/50 focus:border-primary/50 transition-all h-10"
              {...register("nickname")}
            />
            {errors?.nickname && (
              <p className="text-xs text-destructive mt-1">{errors.nickname.message}</p>
            )}
          </div>
          <div className="grid gap-2">
            <Label htmlFor="birthDate">생년월일</Label>
            <Input
              id="birthDate"
              placeholder="YYYY-MM-DD"
              type="text"
              disabled={isLoading}
              className="bg-muted/30 border-border/50 focus:border-primary/50 transition-all h-10"
              {...register("birthDate")}
            />
            {errors?.birthDate && (
              <p className="text-xs text-destructive mt-1">{errors.birthDate.message}</p>
            )}
          </div>
          <div className="grid gap-2">
            <Label htmlFor="password">비밀번호</Label>
            <Input
              id="password"
              placeholder="••••••••"
              type="password"
              disabled={isLoading}
              className="bg-muted/30 border-border/50 focus:border-primary/50 transition-all h-10"
              {...register("password")}
            />
            {errors?.password && (
              <p className="text-xs text-destructive mt-1">{errors.password.message}</p>
            )}
          </div>
          <div className="grid gap-2">
            <Label htmlFor="confirmPassword">비밀번호 확인</Label>
            <Input
              id="confirmPassword"
              placeholder="••••••••"
              type="password"
              disabled={isLoading}
              className="bg-muted/30 border-border/50 focus:border-primary/50 transition-all h-10"
              {...register("confirmPassword")}
            />
            {errors?.confirmPassword && (
              <p className="text-xs text-destructive mt-1">{errors.confirmPassword.message}</p>
            )}
          </div>
          <Button disabled={isLoading} className="h-11 grad-primary hover:opacity-90 transition-opacity text-white font-semibold mt-2">
            {isLoading && (
              <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
            )}
            가입하기
          </Button>
        </div>
      </form>
    </div>
  )
}

# 🎨 Shadcn/ui 가이드

**작성일**: 2026.01.16  
**작성자**: Antigravity  
**문서 버전**: v1.0

---

> ForkLore 프로젝트에서 Shadcn/ui를 효과적으로 사용하기 위한 개발 가이드라인입니다. Tailwind CSS 4와 React 19 환경에 최적화된 사용법을 제공합니다.

## 1. 개요 (Overview)

Shadcn/ui는 전통적인 컴포넌트 라이브러리(npm 설치 방식)가 아니라, 코드를 프로젝트로 직접 가져와서 사용하는 **컴포넌트 컬렉션**입니다. 

- **제어권(Ownership)**: 컴포넌트 코드가 `components/ui` 폴더 내에 직접 존재하므로, 필요에 따라 로직과 스타일을 완전히 수정할 수 있습니다.
- **접근성(Accessibility)**: Radix UI를 기반으로 하여 WAI-ARIA 표준을 준수합니다.
- **스타일링**: Tailwind CSS를 사용하여 선언적으로 디자인을 정의합니다.

---

## 2. 설치 및 설정 (Installation)

### 2.1 초기화

다음 명령어를 사용하여 프로젝트에 Shadcn/ui를 초기화합니다.

```bash
pnpm dlx shadcn@latest init
```

### 2.2 components.json 설정

ForkLore 프로젝트의 표준 설정은 다음과 같습니다.

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "zinc",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "iconLibrary": "lucide"
}
```

---

## 3. 컴포넌트 사용 패턴 (Component Usage)

### 3.1 React 19 패턴

React 19부터는 더 이상 `forwardRef`를 수동으로 작성할 필요가 없습니다. `ref`는 일반 `props`처럼 전달됩니다.

```tsx
// ✅ React 19 방식
export function MyButton({ ref, ...props }: React.ComponentProps<"button">) {
  return <button ref={ref} {...props} />;
}
```

### 3.2 data-slot 스타일링

컴포넌트 내부 요소에 `data-slot` 속성을 부여하여 Tailwind에서 자식 요소를 타겟팅하기 쉽게 구성합니다.

```tsx
<div data-slot="button-container" className="group">
  <button className="group-data-[slot=button-container]:bg-blue-500">
    Click Me
  </button>
</div>
```

### 3.3 cn() 유틸리티

조건부 클래스 결합 및 Tailwind 클래스 병합을 위해 `cn()` 유틸리티를 반드시 사용합니다.

```tsx
import { cn } from "@/lib/utils";

export function Button({ className, variant, ...props }) {
  return (
    <button
      className={cn(
        "base-styles",
        variant === "primary" && "bg-blue-500",
        className
      )}
      {...props}
    />
  );
}
```

---

## 4. 테마 커스터마이징 (Theming)

### 4.1 Tailwind CSS 4 `@theme`

Tailwind CSS 4에서는 CSS 파일 내에서 직접 테마를 정의합니다. `globals.css` 파일에서 OKLCH 색상 시스템을 사용합니다.

```css
@theme {
  --color-background: oklch(100% 0 0);
  --color-foreground: oklch(14.5% 0 0);
  
  --color-primary: oklch(47.2% 0.137 245.5);
  --color-primary-foreground: oklch(98.5% 0 0);
  
  --radius-xl: 1rem;
  --radius-lg: 0.5rem;
}
```

### 4.2 CSS 변수 비교

| 변수명 | 설명 | 예시 (Light) |
| :--- | :--- | :--- |
| `--background` | 페이지 기본 배경색 | `oklch(100% 0 0)` |
| `--foreground` | 기본 텍스트 색상 | `oklch(14.5% 0 0)` |
| `--primary` | 주요 강조 색상 (버튼 등) | `oklch(47.2% 0.137 245.5)` |
| `--destructive` | 위험/삭제 액션 색상 | `oklch(62.8% 0.257 25.7)` |

---

## 5. 확장 및 수정 (Extending Components)

### 5.1 컴포지션 vs 래퍼 (Composition over Wrappers)

복잡한 래퍼 컴포넌트를 만들기보다, Shadcn의 기본 단위(Button, Card 등)를 조합하여 사용하는 것을 지향합니다.

- **Bad**: 모든 기능을 담은 거대한 `CustomModal` 제작
- **Good**: `Dialog`, `DialogContent`, `DialogHeader` 등을 필요한 곳에서 조합

### 5.2 직접 수정 (Direct Modification)

`components/ui`에 생성된 파일은 라이브러리 코드가 아닌 **여러분의 코드**입니다. 프로젝트의 요구사항에 맞게 내부 로직을 직접 수정하는 것을 두려워하지 마세요.

- 예: `Table` 컴포넌트에 특정 호버 효과를 전역적으로 추가하고 싶다면, `components/ui/table.tsx`를 직접 수정합니다.

### 5.3 알림창 선택 (Sonner vs Toast)

| 기능 | 추천 | 이유 |
| :--- | :--- | :--- |
| 일반적인 알림 | `Sonner` | 더 나은 사용자 경험, 간단한 API |
| 복잡한 상호작용 알림 | `Toast` | Radix UI 기반의 정밀한 제어 |

---

## 6. React Hook Form + Zod 연동

Shadcn/ui는 `Form` 컴포넌트를 통해 React Hook Form과 Zod의 강력한 유효성 검사를 지원합니다.

```tsx
"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

const formSchema = z.object({
  username: z.string().min(2, {
    message: "사용자 이름은 2글자 이상이어야 합니다.",
  }),
})

export function ProfileForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
    },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>사용자 이름</FormLabel>
              <FormControl>
                <Input placeholder="antigravity" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">제출</Button>
      </form>
    </Form>
  )
}
```

---

## 문서 끝

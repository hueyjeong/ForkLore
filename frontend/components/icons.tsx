import * as React from "react"
import {
  Github,
  Loader2,
  LucideIcon,
  Moon,
  Sun,
  X,
  User,
  Menu,
  Search,
  Check,
  Eye,
  EyeOff,
  ChevronRight,
  ChevronLeft,
} from "lucide-react"

export type Icon = LucideIcon

export const Icons = {
  spinner: Loader2,
  gitHub: Github,
  google: ({ ...props }: React.ComponentProps<"svg">) => (
    <svg
      aria-hidden="true"
      focusable="false"
      data-prefix="fab"
      data-icon="google"
      role="img"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 48 48"
      {...props}
    >
      <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
      <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
      <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
      <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
      <path fill="none" d="M0 0h48v48H0z" />
    </svg>
  ),
  sun: Sun,
  moon: Moon,
  menu: Menu,
  search: Search,
  user: User,
  close: X,
  check: Check,
  eye: Eye,
  eyeOff: EyeOff,
  chevronRight: ChevronRight,
  chevronLeft: ChevronLeft,
  kakao: ({ ...props }: React.ComponentProps<"svg">) => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      {...props}
    >
      <path d="M12 3C6.48 3 2 6.48 2 10.76c0 2.89 1.96 5.43 4.96 6.81-.22.8-1.42 5.09-1.47 5.27-.05.21.14.36.31.24.23-.16 3.6-2.38 4.22-2.8.63.09 1.28.14 1.95.14 5.52 0 10-3.48 10-7.76S17.52 3 12 3z" />
    </svg>
  ),
}

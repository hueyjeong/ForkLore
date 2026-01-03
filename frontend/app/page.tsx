import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

export default function Home() {
  return (
    <div className="bg-background text-foreground flex min-h-screen flex-col items-center justify-center gap-8 p-24">
      <h1 className="font-serif text-4xl font-bold">ForkLore UI Review</h1>

      <div className="grid w-full max-w-4xl grid-cols-1 gap-8 md:grid-cols-2">
        {/* Buttons Section */}
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Buttons</CardTitle>
            <CardDescription>Various button variants</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-4">
            <Button>Default</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="link">Link</Button>
          </CardContent>
        </Card>

        {/* Inputs Section */}
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Inputs</CardTitle>
            <CardDescription>Input fields and forms</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input type="email" placeholder="Email" />
            <div className="flex w-full max-w-sm items-center space-x-2">
              <Input type="text" placeholder="Search..." />
              <Button type="submit">Subscribe</Button>
            </div>
          </CardContent>
        </Card>

        {/* Dropdown Section */}
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Interactive</CardTitle>
            <CardDescription>Dropdowns and Menus</CardDescription>
          </CardHeader>
          <CardContent>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">Open Menu</Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuLabel>My Account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>Profile</DropdownMenuItem>
                <DropdownMenuItem>Billing</DropdownMenuItem>
                <DropdownMenuItem>Team</DropdownMenuItem>
                <DropdownMenuItem>Subscription</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useMutation } from "@tanstack/react-query"
import { Loader2 } from "lucide-react"
import { toast } from "sonner"

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

import { createLinkRequest } from "@/lib/api/branches.api"

const requestSchema = z.object({
  request_message: z
    .string()
    .min(10, "Message must be at least 10 characters")
    .max(500, "Message must be less than 500 characters"),
})

interface LinkRequestModalProps {
  branchId: number
  trigger: React.ReactNode
}

export function LinkRequestModal({ branchId, trigger }: LinkRequestModalProps) {
  const [open, setOpen] = useState(false)

  const form = useForm<z.infer<typeof requestSchema>>({
    resolver: zodResolver(requestSchema),
    defaultValues: {
      request_message: "",
    },
  })

  const { mutate: sendRequest, isPending } = useMutation({
    mutationFn: (values: z.infer<typeof requestSchema>) =>
      createLinkRequest(branchId, values),
    onSuccess: () => {
      toast.success("Link request sent successfully")
      setOpen(false)
      form.reset()
    },
    onError: (error) => {
      toast.error("Failed to send link request")
      console.error(error)
    },
  })

  function onSubmit(values: z.infer<typeof requestSchema>) {
    sendRequest(values)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Request Link</DialogTitle>
          <DialogDescription>
            Request to link this branch to the main storyline.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="request_message"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Message</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Explain why this branch should be linked..."
                      className="resize-none"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="submit" disabled={isPending}>
                {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Send Request
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

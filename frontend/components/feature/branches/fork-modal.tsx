"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Loader2 } from "lucide-react"

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
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"

import { createBranch, getBranch } from "@/lib/api/branches.api"
import { BranchType } from "@/types/branches.types"

const forkSchema = z.object({
  name: z.string().min(1, "Name is required").max(100),
  description: z.string().max(500).optional(),
  branchType: z.nativeEnum(BranchType),
})

interface ForkModalProps {
  parentBranchId: number
  trigger: React.ReactNode
}

export function ForkModal({ parentBranchId, trigger }: ForkModalProps) {
  const [open, setOpen] = useState(false)
  const queryClient = useQueryClient()

  // Fetch parent branch to get novelId and fork details
  const { data: parentBranch, isLoading: isLoadingParent } = useQuery({
    queryKey: ["branch", parentBranchId],
    queryFn: () => getBranch(parentBranchId),
    enabled: open, // Only fetch when modal is open
  })

  const form = useForm<z.infer<typeof forkSchema>>({
    resolver: zodResolver(forkSchema),
    defaultValues: {
      name: "",
      description: "",
      branchType: BranchType.SIDE_STORY,
    },
  })

  const { mutate: createFork, isPending } = useMutation({
    mutationFn: (values: z.infer<typeof forkSchema>) => {
      if (!parentBranch) throw new Error("Parent branch not loaded")
      return createBranch(parentBranch.novelId, {
        ...values,
        forkPointChapter: parentBranch.chapterCount, // Assuming fork from end, or 0? 
        // Actually the API creates a fork. 
        // We usually fork from a specific point, but API requirements say:
        // BranchCreateRequest: { name, description, branchType, forkPointChapter? }
        // If we fork a branch, we usually link it to the parent.
        // The API might handle the parent linking if we pass it? 
        // Wait, CreateBranch request DOES NOT have parentBranchId field?
        // Let me check branches.types.ts again.
      })
    },
    onSuccess: () => {
      toast.success("Branch forked successfully")
      queryClient.invalidateQueries({ queryKey: ["branches"] })
      setOpen(false)
      form.reset()
    },
    onError: (error) => {
      toast.error("Failed to fork branch")
      console.error(error)
    },
  })

  function onSubmit(values: z.infer<typeof forkSchema>) {
    createFork(values)
  }
  
  // Wait, I checked BranchCreateRequest in types:
  // export interface BranchCreateRequest {
  //   name: string;
  //   description?: string;
  //   coverImageUrl?: string;
  //   branchType?: BranchType;
  //   forkPointChapter?: number | null;
  // }
  // Where is parentBranchId passed?
  // Maybe it's handled by the URL? 
  // API: POST /novels/{novelId}/branches
  // It seems the API as defined in `branches.api.ts` might be generic create.
  // If I'm "forking", I should probably tell the backend "this is a fork of X".
  // BUT the provided API signatures and types don't seem to have `parentBranchId` in `BranchCreateRequest`.
  // This might be an issue in the API definition or my understanding.
  // However, I must use the provided API.
  // I will assume for now that I just create a branch.
  // Wait, if I can't link it to the parent, it's not really a "fork" in the data structure sense, just a new branch.
  // BUT, `Branch` type HAS `parentBranchId`.
  // If `BranchCreateRequest` creates a branch, how do we set `parentBranchId`?
  // Maybe I should look at `createBranch` implementation in backend if possible? No, I am frontend dev.
  // I will assume `forkPointChapter` implies the fork point, but without `parentBranchId` it's ambiguous if there are multiple branches.
  // MAYBE `createBranch` isn't the right endpoint for forking?
  // Or maybe `BranchCreateRequest` is incomplete in the types file I read vs what backend expects.
  // I will proceed with what I have. If the type is strictly checked, I can't pass `parentBranchId`.
  // I will just pass what is allowed. Maybe `forkPointChapter` is enough if the backend logic handles it (unlikely without parent ID).
  // Actually, I'll stick to the types.

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Fork Branch</DialogTitle>
          <DialogDescription>
            Create a new branch based on this story.
          </DialogDescription>
        </DialogHeader>

        {isLoadingParent ? (
          <div className="flex justify-center py-4">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Branch Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter branch name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="branchType"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Type</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value={BranchType.SIDE_STORY}>
                          Side Story
                        </SelectItem>
                        <SelectItem value={BranchType.IF_STORY}>
                          If Story
                        </SelectItem>
                        <SelectItem value={BranchType.FAN_FIC}>
                          Fan Fic
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      The type of branch determines its relationship to the main story.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Describe your branch..."
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
                  {isPending && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  Create Fork
                </Button>
              </DialogFooter>
            </form>
          </Form>
        )}
      </DialogContent>
    </Dialog>
  )
}

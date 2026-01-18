import { z } from 'zod';

// Enums from types/novels.types.ts
export const GenreEnum = z.enum([
  'FANTASY', 'ROMANCE', 'ACTION', 'THRILLER', 'MYSTERY',
  'SF', 'HISTORY', 'MODERN', 'MARTIAL', 'GAME'
]);

export const AgeRatingEnum = z.enum(['ALL', '12', '15', '19']);

export const NovelStatusEnum = z.enum(['ONGOING', 'COMPLETED', 'HIATUS']);

// Enums from types/chapters.types.ts
export const ChapterStatusEnum = z.enum(['DRAFT', 'SCHEDULED', 'PUBLISHED']);
export const AccessTypeEnum = z.enum(['FREE', 'SUBSCRIPTION']);

// Enums from types/subscription.types.ts
export const PlanTypeEnum = z.enum(['BASIC', 'PREMIUM']);
export const SubscriptionStatusEnum = z.enum(['ACTIVE', 'CANCELLED', 'EXPIRED']);

// User Schema (UserResponse from auth.types.ts)
export const UserSchema = z.object({
  id: z.number(),
  email: z.string().email(),
  nickname: z.string(),
  profileImageUrl: z.string().optional(),
  birthDate: z.string().optional(),
  role: z.enum(['READER', 'AUTHOR', 'ADMIN']),
  authProvider: z.enum(['LOCAL', 'GOOGLE', 'KAKAO']),
});

// Author Schema (from novels.types.ts)
export const AuthorSchema = z.object({
  id: z.number(),
  nickname: z.string(),
});

// Novel Schema (from novels.types.ts)
export const NovelSchema = z.object({
  id: z.number(),
  title: z.string(),
  description: z.string(),
  cover_image_url: z.string(),
  genre: GenreEnum,
  age_rating: AgeRatingEnum,
  status: NovelStatusEnum,
  is_exclusive: z.boolean(),
  is_premium: z.boolean(),
  allow_branching: z.boolean(),
  total_view_count: z.number(),
  total_like_count: z.number(),
  total_chapter_count: z.number(),
  branch_count: z.number(),
  linked_branch_count: z.number(),
  author: AuthorSchema,
  created_at: z.string(),
  updated_at: z.string(),
});

// ChapterNav Schema (from chapters.types.ts)
export const ChapterNavSchema = z.object({
  id: z.number(),
  chapter_number: z.number(),
  title: z.string(),
});

// Chapter Schema (from chapters.types.ts)
export const ChapterSchema = z.object({
  id: z.number(),
  chapter_number: z.number(),
  title: z.string(),
  content_html: z.string(),
  word_count: z.number(),
  status: ChapterStatusEnum,
  access_type: AccessTypeEnum,
  price: z.number(),
  scheduled_at: z.string().nullable(),
  published_at: z.string().nullable(),
  view_count: z.number(),
  like_count: z.number(),
  comment_count: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
  prev_chapter: ChapterNavSchema.nullable(),
  next_chapter: ChapterNavSchema.nullable(),
});

// Subscription Schema (from subscription.types.ts)
export const SubscriptionSchema = z.object({
  id: z.number(),
  plan_type: PlanTypeEnum,
  status: SubscriptionStatusEnum,
  started_at: z.string(),
  expires_at: z.string(),
  cancelled_at: z.string().nullable(),
  auto_renew: z.boolean(),
  created_at: z.string(),
});

// Type Exports
export type MockUser = z.infer<typeof UserSchema>;
export type MockNovel = z.infer<typeof NovelSchema>;
export type MockChapter = z.infer<typeof ChapterSchema>;
export type MockSubscription = z.infer<typeof SubscriptionSchema>;

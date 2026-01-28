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
  coverImageUrl: z.string(),
  genre: GenreEnum,
  ageRating: AgeRatingEnum,
  status: NovelStatusEnum,
  isExclusive: z.boolean(),
  isPremium: z.boolean(),
  allowBranching: z.boolean(),
  totalViewCount: z.number(),
  totalLikeCount: z.number(),
  totalChapterCount: z.number(),
  branchCount: z.number(),
  linkedBranchCount: z.number(),
  author: AuthorSchema,
  createdAt: z.string(),
  updatedAt: z.string(),
});

// ChapterNav Schema (from chapters.types.ts)
export const ChapterNavSchema = z.object({
  id: z.number(),
  chapterNumber: z.number(),
  title: z.string(),
});

// Chapter Schema (from chapters.types.ts)
export const ChapterSchema = z.object({
  id: z.number(),
  chapterNumber: z.number(),
  title: z.string(),
  contentHtml: z.string(),
  wordCount: z.number(),
  status: ChapterStatusEnum,
  accessType: AccessTypeEnum,
  price: z.number(),
  scheduledAt: z.string().nullable(),
  publishedAt: z.string().nullable(),
  viewCount: z.number(),
  likeCount: z.number(),
  commentCount: z.number(),
  createdAt: z.string(),
  updatedAt: z.string(),
  prevChapter: ChapterNavSchema.nullable(),
  nextChapter: ChapterNavSchema.nullable(),
});

// Subscription Schema (from subscription.types.ts)
export const SubscriptionSchema = z.object({
  id: z.number(),
  planType: PlanTypeEnum,
  status: SubscriptionStatusEnum,
  startedAt: z.string(),
  expiresAt: z.string(),
  cancelledAt: z.string().nullable(),
  autoRenew: z.boolean(),
  createdAt: z.string(),
});

// Type Exports
export type MockUser = z.infer<typeof UserSchema>;
export type MockNovel = z.infer<typeof NovelSchema>;
export type MockChapter = z.infer<typeof ChapterSchema>;
export type MockSubscription = z.infer<typeof SubscriptionSchema>;

// Enums from types/branches.types.ts
export const BranchTypeEnum = z.enum(['MAIN', 'SIDE_STORY', 'FAN_FIC', 'IF_STORY']);
export const BranchVisibilityEnum = z.enum(['PRIVATE', 'PUBLIC', 'LINKED']);
export const CanonStatusEnum = z.enum(['NON_CANON', 'CANDIDATE', 'MERGED']);

// Branch Schema (from branches.types.ts)
export const BranchSchema = z.object({
  id: z.number(),
  novelId: z.number(),
  name: z.string(),
  description: z.string(),
  coverImageUrl: z.string(),
  isMain: z.boolean(),
  branchType: BranchTypeEnum,
  visibility: BranchVisibilityEnum,
  canonStatus: CanonStatusEnum,
  parentBranchId: z.number().nullable(),
  forkPointChapter: z.number().nullable(),
  voteCount: z.number(),
  voteThreshold: z.number(),
  viewCount: z.number(),
  chapterCount: z.number(),
  author: AuthorSchema,
  createdAt: z.string(),
  updatedAt: z.string(),
});

export type MockBranch = z.infer<typeof BranchSchema>;

// Wiki Schemas (from wiki.types.ts)
export const WikiTagSchema = z.object({
  id: z.number(),
  name: z.string(),
  color: z.string(),
  icon: z.string(),
  description: z.string(),
  displayOrder: z.number(),
  createdAt: z.string(),
});

export const WikiSnapshotSchema = z.object({
  id: z.number(),
  content: z.string(),
  validFromChapter: z.number(),
  contributorType: z.enum(['USER', 'AI']),
  createdAt: z.string(),
});

export const WikiEntrySchema = z.object({
  id: z.number(),
  name: z.string(),
  imageUrl: z.string(),
  firstAppearance: z.number().nullable(),
  hiddenNote: z.string(),
  aiMetadata: z.record(z.string(), z.unknown()).nullable(),
  tags: z.array(WikiTagSchema),
  snapshots: z.array(WikiSnapshotSchema),
  snapshot: WikiSnapshotSchema.nullable(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

export type MockWikiEntry = z.infer<typeof WikiEntrySchema>;

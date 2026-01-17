export interface NovelBase {
  id: string | number;
  title: string;
  author: string;
  coverUrl: string;
  views: string;
  rating: number;
  status: '연재중' | '완결';
  tags: string[];
  description: string;
  episodeCount: number;
  recommendCount: number;
  isExclusive: boolean;
  isPremium: boolean;
  updatedAt: string;
}

export interface Novel extends NovelBase {
  id: string;
  genre: string;
}

export interface RankingNovel extends NovelBase {
  id: number;
}

export interface CommunityPost {
  id: string;
  title: string;
  author: string;
  category: '자유' | '작품토론' | '공지';
  commentCount: number;
  likeCount: number;
  createdAt: string;
  isPinned: boolean;
}

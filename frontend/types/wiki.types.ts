import { PageParams } from './common';

export interface WikiTag {
  id: number;
  name: string;
  category: 'CHARACTER' | 'SETTING' | 'EVENT' | 'ITEM' | 'OTHER';
  description?: string;
  color?: string; // Hex color
}

export interface WikiEntry {
  id: number;
  branchId: number;
  title: string;
  content: string; // Markdown
  tags: WikiTag[];
  isSpoiler: boolean; // Based on spoiler filter
  createdAt: string;
  updatedAt: string;
}

export interface WikiSnapshot {
  id: number;
  wikiId: number;
  chapterId: number; // Snapshot at this chapter
  content: string;
  createdAt: string;
}

export interface CreateWikiRequest {
  branchId: number;
  title: string;
  content: string;
  tagIds: number[];
}

export interface UpdateWikiRequest {
  content: string;
  tagIds?: number[];
}

export interface WikiListParams extends PageParams {
  branchId: number;
  chapterId?: number; // Filter by spoiler scope
  tagId?: number;
  search?: string;
}

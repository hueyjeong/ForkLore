import { Page, Route } from '@playwright/test';
import {
  MockUser, MockNovel, MockChapter,
  MockSubscription,
  MockWikiEntry,
  MockBranch
} from '../fixtures/mock-schemas';

interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  serverTime: string;
}

interface PaginatedResponse<T> {
  results: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

const defaultUser: MockUser = {
  id: 1,
  email: 'test@example.com',
  nickname: 'TestReader',
  role: 'READER',
  authProvider: 'LOCAL',
};

const defaultNovel: MockNovel = {
  id: 1,
  title: 'Test Novel',
  description: 'A riveting tale of testing.',
  cover_image_url: 'https://via.placeholder.com/300x450',
  genre: 'FANTASY',
  age_rating: 'ALL',
  status: 'ONGOING',
  is_exclusive: false,
  is_premium: false,
  allow_branching: true,
  total_view_count: 1000,
  total_like_count: 50,
  total_chapter_count: 10,
  branch_count: 2,
  linked_branch_count: 5,
  author: { id: 100, nickname: 'AuthorOne' },
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

const defaultChapter: MockChapter = {
  id: 10,
  chapter_number: 1,
  title: 'Chapter 1: The Beginning',
  content_html: '<p>Once upon a time...</p>',
  word_count: 500,
  status: 'PUBLISHED',
  access_type: 'FREE',
  price: 0,
  scheduled_at: null,
  published_at: new Date().toISOString(),
  view_count: 100,
  like_count: 10,
  comment_count: 5,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  prev_chapter: null,
  next_chapter: { id: 11, chapter_number: 2, title: 'Chapter 2' },
};

export class MockHelper {
  constructor(private page: Page) {}

  /**
   * Mocks an API route with typed response
   */
  async mockRoute<T>(
    urlPattern: string | RegExp,
    data: T,
    statusCode = 200
  ): Promise<void> {
    await this.page.route(urlPattern, async (route) => {
      const response: ApiResponse<T> = {
        success: statusCode >= 200 && statusCode < 300,
        data,
        serverTime: new Date().toISOString(),
      };

      await route.fulfill({
        status: statusCode,
        contentType: 'application/json',
        body: JSON.stringify(response),
      });
    });
  }

  /**
   * Mocks the generic user profile endpoint
   */
  async mockUser(overrides: Partial<MockUser> = {}) {
    await this.mockRoute('/users/me', { ...defaultUser, ...overrides });
  }

  /**
   * Mocks a specific novel detail endpoint
   */
  async mockNovel(id: number | string, overrides: Partial<MockNovel> = {}) {
    const numericId = Number(id);
    await this.mockRoute(new RegExp(`/novels/${numericId}$`), { 
      ...defaultNovel, 
      id: numericId, 
      ...overrides 
    });
  }

  /**
   * Mocks the novels list endpoint with pagination
   */
  async mockNovelList(novels: MockNovel[], page = 1, limit = 20) {
    const response: PaginatedResponse<MockNovel> = {
      results: novels,
      total: novels.length,
      page,
      limit,
      totalPages: Math.ceil(novels.length / limit),
      hasNext: false,
      hasPrev: false,
    };
    
    // We match the base /novels endpoint but careful not to match /novels/:id
    // This regex looks for /novels optionally followed by query params, but not followed by /something
    await this.mockRoute(/\/novels(\?.*)?$/, response);
  }

  /**
   * Mocks a specific chapter detail endpoint
   */
  async mockChapter(id: number | string, overrides: Partial<MockChapter> = {}) {
    const numericId = Number(id);
    await this.mockRoute(new RegExp(`/chapters/${numericId}$`), { 
      ...defaultChapter, 
      id: numericId, 
      ...overrides 
    });
  }

  /**
   * Mocks chapters list for a branch
   */
  async mockChapterList(branchId: number | string, chapters: MockChapter[]) {
    const response: PaginatedResponse<MockChapter> = {
      results: chapters,
      total: chapters.length,
      page: 1,
      limit: 20,
      totalPages: 1,
      hasNext: false,
      hasPrev: false,
    };
    await this.mockRoute(new RegExp(`/branches/${branchId}/chapters`), response);
  }

  /**
   * Mocks wikis list for a branch
   */
  async mockWikiList(branchId: number | string, wikis: MockWikiEntry[]) {
    const response: PaginatedResponse<MockWikiEntry> = {
      results: wikis,
      total: wikis.length,
      page: 1,
      limit: 20,
      totalPages: 1,
      hasNext: false,
      hasPrev: false,
    };
    await this.mockRoute(new RegExp(`/branches/${branchId}/wikis`), response);
  }

  /**
   * Mocks branch creation endpoint
   */
  async mockBranchCreation(novelId: number | string, newBranch: MockBranch) {
    const numericId = Number(novelId);
    // Use exact match or regex depending on how strict we want to be
    await this.mockRoute(new RegExp(`/novels/${numericId}/branches$`), newBranch, 201);
  }

  /**
   * Mocks branch creation conflict (409)
   */
  async mockBranchConflict(novelId: number | string) {
    const numericId = Number(novelId);
    await this.page.route(new RegExp(`/novels/${numericId}/branches$`), async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 409,
          contentType: 'application/json',
          body: JSON.stringify({
            success: false,
            data: null,
            message: 'Concurrent fork detected',
            serverTime: new Date().toISOString(),
          }),
        });
      } else {
        await route.fallback();
      }
    });
  }

  /**
   * Mocks branches list for a novel
   */
  async mockBranchList(novelId: number | string, branches: MockBranch[]) {
    const numericId = Number(novelId);
    const response: PaginatedResponse<MockBranch> = {
      results: branches,
      total: branches.length,
      page: 1,
      limit: 20,
      totalPages: 1,
      hasNext: false,
      hasPrev: false,
    };
    await this.mockRoute(new RegExp(`/novels/${numericId}/branches(\\?.*)?$`), response);
  }
}

import { Page } from '@playwright/test';
import {
  MockUser, MockNovel, MockChapter,
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
  coverImageUrl: 'https://via.placeholder.com/300x450',
  genre: 'FANTASY',
  ageRating: 'ALL',
  status: 'ONGOING',
  isExclusive: false,
  isPremium: false,
  allowBranching: true,
  totalViewCount: 1000,
  totalLikeCount: 50,
  totalChapterCount: 10,
  branchCount: 2,
  linkedBranchCount: 5,
  author: { id: 100, nickname: 'AuthorOne' },
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

const defaultChapter: MockChapter = {
  id: 10,
  chapterNumber: 1,
  title: 'Chapter 1: The Beginning',
  contentHtml: '<p>Once upon a time...</p>',
  wordCount: 500,
  status: 'PUBLISHED',
  accessType: 'FREE',
  price: 0,
  scheduledAt: null,
  publishedAt: new Date().toISOString(),
  viewCount: 100,
  likeCount: 10,
  commentCount: 5,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  prevChapter: null,
  nextChapter: { id: 11, chapterNumber: 2, title: 'Chapter 2' },
};

export class MockHelper {
  constructor(private page: Page) {}

  /**
   * Mocks an API route with typed response
   */
  async mockRoute<T>(
    urlPattern: string | RegExp,
    data: T,
    statusCode = 200,
    message?: string
  ): Promise<void> {
    await this.page.route(urlPattern, async (route) => {
      const response: ApiResponse<T> = {
        success: statusCode >= 200 && statusCode < 300,
        data,
        serverTime: new Date().toISOString(),
        ...(message && { message }),
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
    await this.mockRoute(new RegExp(`/novels/${numericId}/?$`), { 
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
    await this.mockRoute(/\/novels\/?(\?.*)?$/, response);
  }

  /**
   * Mocks a specific chapter detail endpoint
   */
  async mockChapter(id: number | string, overrides: Partial<MockChapter> = {}) {
    const numericId = Number(id);
    await this.mockRoute(new RegExp(`/chapters/${numericId}/?$`), { 
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
    await this.mockRoute(new RegExp(`/branches/${branchId}/chapters/?$`), response);
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
    await this.mockRoute(new RegExp(`/branches/${branchId}/wikis/?$`), response);
  }

  /**
   * Mocks branch creation endpoint
   */
  async mockBranchCreation(novelId: number | string, newBranch: MockBranch) {
    const numericId = Number(novelId);
    const pattern = new RegExp(`/novels/${numericId}/branches/?$`);

    await this.page.route(pattern, async (route) => {
      if (route.request().method() !== 'POST') {
        await route.fallback();
        return;
      }

      const response: ApiResponse<MockBranch> = {
        success: true,
        data: newBranch,
        serverTime: new Date().toISOString(),
      };

      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(response),
      });
    });
  }

  /**
   * Mocks branch creation conflict (409)
   */
  async mockBranchConflict(novelId: number | string) {
    const numericId = Number(novelId);
    await this.page.route(new RegExp(`/novels/${numericId}/branches/?$`), async (route) => {
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
    const pattern = new RegExp(`/novels/${numericId}/branches/?(\\?.*)?$`);

    const response: PaginatedResponse<MockBranch> = {
      results: branches,
      total: branches.length,
      page: 1,
      limit: 20,
      totalPages: 1,
      hasNext: false,
      hasPrev: false,
    };

    await this.page.route(pattern, async (route) => {
      if (route.request().method() !== 'GET') {
        await route.fallback();
        return;
      }

      const apiResponse: ApiResponse<PaginatedResponse<MockBranch>> = {
        success: true,
        data: response,
        serverTime: new Date().toISOString(),
      };

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(apiResponse),
      });
    });
  }
}

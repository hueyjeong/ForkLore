import { test, expect } from '@playwright/test';
import { MockHelper } from '../utils/mock-helper';
import { ReaderPage } from '../pages/reader.page';
import { 
  MockBranch, 
  BranchTypeEnum, 
  BranchVisibilityEnum, 
  CanonStatusEnum 
} from '../fixtures/mock-schemas';

test.describe('Fork Lifecycle', () => {
  let mockHelper: MockHelper;
  let readerPage: ReaderPage;

  test.beforeEach(async ({ page }) => {
    mockHelper = new MockHelper(page);
    readerPage = new ReaderPage(page);
    
    // Default mocks
    await mockHelper.mockUser(); // Logged in user
    await mockHelper.mockNovel('1');
    await mockHelper.mockChapter('10', { 
      id: 10, 
      title: 'Chapter 1', 
      chapterNumber: 1 
    });
    
    // Mock existing branches (Main branch)
    const mainBranch: MockBranch = {
      id: 100,
      novelId: 1,
      name: 'Main Story',
      description: 'The original story',
      coverImageUrl: 'https://example.com/cover.jpg',
      isMain: true,
      branchType: BranchTypeEnum.enum.MAIN,
      visibility: BranchVisibilityEnum.enum.PUBLIC,
      canonStatus: CanonStatusEnum.enum.MERGED,
      parentBranchId: null,
      forkPointChapter: null,
      voteCount: 100,
      voteThreshold: 0,
      viewCount: 1000,
      chapterCount: 10,
      author: { id: 100, nickname: 'AuthorOne' },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    await mockHelper.mockBranchList('1', [mainBranch]);
  });

  // TODO: #239 - Branch creation flow requires backend fork endpoint implementation
  test.fixme('Scenario 1: Successful Forking', async ({ page }) => {
    const newBranch: MockBranch = {
      id: 101,
      novelId: 1,
      name: 'My Fork',
      description: 'A new perspective',
      coverImageUrl: 'https://example.com/cover.jpg',
      isMain: false,
      branchType: BranchTypeEnum.enum.SIDE_STORY,
      visibility: BranchVisibilityEnum.enum.PUBLIC,
      canonStatus: CanonStatusEnum.enum.NON_CANON,
      parentBranchId: 100,
      forkPointChapter: 1,
      voteCount: 0,
      voteThreshold: 0,
      viewCount: 0,
      chapterCount: 0,
      author: { id: 1, nickname: 'TestReader' },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    // Mock successful creation
    await mockHelper.mockBranchCreation('1', newBranch);

    // Navigate to Reader
    await readerPage.goto('1', '10');

    // Click "Fork" button (Assuming it's available in the reader interface)
    // We might need to open a menu first if it's hidden, but expecting a visible button for now
    await page.getByRole('button', { name: 'Fork' }).click();

    // Fill Fork Modal
    await page.getByLabel('Title').fill('My Fork');
    await page.getByLabel('Description').fill('A new perspective');
    
    // Select Branch Type if available, defaulting to generic inputs for now
    
    // Submit
    await page.getByRole('button', { name: /create|fork/i }).click();

    // Verify API call was made (implicitly verified by the mock returning success and UI reacting)
    
    // Verify UI feedback
    // Expecting a toast or some success indicator
    await expect(page.getByText(/created successfully|fork created/i)).toBeVisible();
  });

  // TODO: #239 - Branch creation flow requires backend fork endpoint implementation
  test.fixme('Scenario 2: Concurrent Forking Conflict', async ({ page }) => {
    // Mock conflict (409)
    await mockHelper.mockBranchConflict('1');

    // Navigate to Reader
    await readerPage.goto('1', '10');

    // Click "Fork" button
    await page.getByRole('button', { name: 'Fork' }).click();

    // Fill Modal
    await page.getByLabel('Title').fill('My Fork');
    await page.getByLabel('Description').fill('Conflict Test');

    // Submit
    await page.getByRole('button', { name: /create|fork/i }).click();

    // Verify error message
    await expect(page.getByText(/Concurrent fork detected|already exists/i)).toBeVisible();
  });
});

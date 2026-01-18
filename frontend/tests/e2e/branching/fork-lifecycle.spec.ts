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
      chapter_number: 1 
    });
    
    // Mock existing branches (Main branch)
    const mainBranch: MockBranch = {
      id: 100,
      novel_id: 1,
      name: 'Main Story',
      description: 'The original story',
      cover_image_url: 'https://example.com/cover.jpg',
      is_main: true,
      branch_type: BranchTypeEnum.enum.MAIN,
      visibility: BranchVisibilityEnum.enum.PUBLIC,
      canon_status: CanonStatusEnum.enum.MERGED,
      parent_branch_id: null,
      fork_point_chapter: null,
      vote_count: 100,
      vote_threshold: 0,
      view_count: 1000,
      chapter_count: 10,
      author: { id: 100, nickname: 'AuthorOne' },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    await mockHelper.mockBranchList('1', [mainBranch]);
  });

  test.fixme('Scenario 1: Successful Forking', async ({ page }) => {
    const newBranch: MockBranch = {
      id: 101,
      novel_id: 1,
      name: 'My Fork',
      description: 'A new perspective',
      cover_image_url: 'https://example.com/cover.jpg',
      is_main: false,
      branch_type: BranchTypeEnum.enum.SIDE_STORY,
      visibility: BranchVisibilityEnum.enum.PUBLIC,
      canon_status: CanonStatusEnum.enum.NON_CANON,
      parent_branch_id: 100,
      fork_point_chapter: 1,
      vote_count: 0,
      vote_threshold: 0,
      view_count: 0,
      chapter_count: 0,
      author: { id: 1, nickname: 'TestReader' },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
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

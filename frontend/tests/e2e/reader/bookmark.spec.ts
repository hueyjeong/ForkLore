import { test, expect } from '@playwright/test';
import { MockHelper } from '../utils/mock-helper';
import { ReaderPage } from '../pages/reader.page';
import { MockBookmark } from '../fixtures/mock-schemas';

test.describe('Bookmark Functionality', () => {
  let mockHelper: MockHelper;
  let readerPage: ReaderPage;

  const defaultBookmark: MockBookmark = {
    id: 1,
    chapter_id: 10,
    user: {
      id: 1,
      nickname: 'TestReader',
    },
    novel: {
      id: 1,
      title: 'Test Novel',
      cover_image_url: 'https://via.placeholder.com/300x450',
    },
    chapter: {
      id: 10,
      chapter_number: 1,
      title: 'Chapter 1: The Beginning',
    },
    created_at: new Date().toISOString(),
  };

  test.beforeEach(async ({ page }) => {
    mockHelper = new MockHelper(page);
    readerPage = new ReaderPage(page);

    await mockHelper.mockUser();
    await mockHelper.mockNovel(1, { title: 'Test Novel' });
    await mockHelper.mockChapter(10, { 
      id: 10, 
      chapter_number: 1, 
      title: 'Chapter 1: The Beginning',
      content_html: '<p>Once upon a time...</p>'
    });
  });

  // TODO(#241): Blocked - Bookmark button not wired to API in reader-view.tsx
  // Waiting on: Bookmark API integration in ReaderView component
  // Tracking: https://github.com/hueyjeong/ForkLore/issues/241
  test.fixme('should add bookmark on chapter page', async ({ page }) => {
    await mockHelper.mockBookmarkCreate(10, defaultBookmark);

    await readerPage.goto(1, 10);

    const bookmarkButton = page.locator('button:has(.lucide-bookmark)');
    await expect(bookmarkButton).toBeVisible();

    await bookmarkButton.click();

    const toast = page.getByRole('alert');
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('Bookmark added');
  });

  test.fixme('should view bookmarks in library tab', async ({ page }) => {
    await mockHelper.mockBookmarkList([defaultBookmark]);

    await page.goto('/library');

    const bookmarksTab = page.getByRole('tab', { name: /Bookmarks/i });
    await expect(bookmarksTab).toBeVisible();
    await bookmarksTab.click();

    await expect(page.getByText('Test Novel')).toBeVisible();
    await expect(page.getByText('Chapter 1: The Beginning')).toBeVisible();
  });

  test.fixme('should remove bookmark and verify removal', async ({ page }) => {
    await mockHelper.mockBookmarkCreate(10, defaultBookmark);
    await mockHelper.mockBookmarkDelete(1);

    await readerPage.goto(1, 10);

    const bookmarkButton = page.locator('button:has(.lucide-bookmark)');
    await bookmarkButton.click();

    const toast = page.getByRole('alert');
    await expect(toast).toContainText('Bookmark added');

    await bookmarkButton.click();

    await expect(toast).toContainText('Bookmark removed');

    await page.goto('/library');

    const bookmarksTab = page.getByRole('tab', { name: /Bookmarks/i });
    await bookmarksTab.click();

    await mockHelper.mockBookmarkList([]);

    await expect(page.getByText('Test Novel')).not.toBeVisible();
    await expect(page.getByText('No bookmarks')).toBeVisible();
  });
});

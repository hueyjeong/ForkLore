import { test, expect } from '@playwright/test';
import { MockHelper } from '../utils/mock-helper';
import { ReaderPage } from '../pages/reader.page';
import { MockWikiEntry } from '../fixtures/mock-schemas';

test.describe('Reader Context Awareness', () => {
  let mockHelper: MockHelper;
  let readerPage: ReaderPage;

  const defaultWikiEntry: MockWikiEntry = {
    id: 1,
    name: 'Test Wiki',
    imageUrl: 'https://via.placeholder.com/150',
    firstAppearance: 1,
    hiddenNote: '',
    aiMetadata: null,
    tags: [],
    snapshots: [],
    snapshot: null,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  test.beforeEach(async ({ page }) => {
    mockHelper = new MockHelper(page);
    readerPage = new ReaderPage(page);

    // Mock User
    await mockHelper.mockUser();
    
    // Mock Novel (ID 1)
    await mockHelper.mockNovel(1, { title: 'Context Novel', allowBranching: true });
    
    // Mock Chapters
    const chapter1 = { 
        id: 10, 
        chapterNumber: 1, 
        title: 'Chapter 1',
        contentHtml: '<p>Once upon a time in a land far away.</p>' 
    };
    const chapter2 = { 
        id: 11, 
        chapterNumber: 2, 
        title: 'Chapter 2',
        contentHtml: '<p>The story continues...</p>'
    };
    await mockHelper.mockChapter(10, chapter1);
    await mockHelper.mockChapter(11, chapter2);
  });

  // TODO(#239): Blocked - Wiki context filtering not integrated in frontend
  // Waiting on: WikiService.list current_chapter parameter implementation
  // Tracking: https://github.com/hueyjeong/ForkLore/issues/239
  test.fixme('Wiki Visibility by Chapter', async ({ page }) => {
     // Mock 2 Wiki Entries
     const entryA: MockWikiEntry = { 
         ...defaultWikiEntry, 
         id: 1, 
         name: 'Wiki A', 
         firstAppearance: 1 
     };
     const entryB: MockWikiEntry = { 
         ...defaultWikiEntry, 
         id: 2, 
         name: 'Wiki B', 
         firstAppearance: 2 
     };

     // Scenario: Reader at Chapter 1
     // Mock API response for Wikis (Simulating Server-Side Filtering: Only A is returned)
     await mockHelper.mockWikiList(1, [entryA]); 
     
     // Navigate to Chapter 1
     await readerPage.goto(1, 10);
     
     // Verify Wiki A is visible, B is not
     await expect(page.getByText('Wiki A')).toBeVisible(); 
     await expect(page.getByText('Wiki B')).not.toBeVisible();

     // Scenario: Reader at Chapter 2
     // Mock API response for Wikis (Both A and B returned)
     await mockHelper.mockWikiList(1, [entryA, entryB]);
     
     // Navigate to Chapter 2
     await readerPage.goto(1, 11);
     
     // Verify both are visible
     await expect(page.getByText('Wiki A')).toBeVisible();
     await expect(page.getByText('Wiki B')).toBeVisible();
  });

  // TODO(#240): Blocked - Paragraph-level comment UI not implemented
  // Waiting on: ParagraphCommentModal component
  // Tracking: https://github.com/hueyjeong/ForkLore/issues/240
  test.fixme('Paragraph Comment', async ({ page }) => {
    // Navigate to Chapter 1
    await readerPage.goto(1, 10);
    
    // Select text "Once upon a time"
    await readerPage.selectText('Once upon a time');
    
    // Verify "Add Comment" tooltip/button appears
    // We expect a button with "Comment" or similar text/aria-label
    const commentButton = page.getByRole('button', { name: /Comment/i }).first();
    await expect(commentButton).toBeVisible();
  });
});

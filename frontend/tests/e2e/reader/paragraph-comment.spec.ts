import { test, expect } from '@playwright/test';
import { MockHelper } from '../utils/mock-helper';
import { ReaderPage } from '../pages/reader.page';

interface UserBrief {
  id: number
  nickname: string
  profile_image: string | null
}

interface Comment {
  id: number
  user: UserBrief
  content: string
  is_spoiler: boolean
  is_pinned: boolean
  like_count: number
  paragraph_index: number | null
  selection_start: number | null
  selection_end: number | null
  quoted_text: string
  parent_id: number | null
  reply_count: number
  created_at: string
  updated_at: string
}

test.describe('Paragraph Comments', () => {
  let mockHelper: MockHelper;
  let readerPage: ReaderPage;

  const mockUser: UserBrief = {
    id: 1,
    nickname: 'TestReader',
    profile_image: 'https://via.placeholder.com/150',
  };

  const createMockComment = (
    overrides: Partial<Comment> = {}
  ): Comment => ({
    id: 1,
    user: mockUser,
    content: 'This is a great paragraph!',
    is_spoiler: false,
    is_pinned: false,
    like_count: 5,
    paragraph_index: 0,
    selection_start: 0,
    selection_end: 20,
    quoted_text: 'Once upon a time',
    parent_id: null,
    reply_count: 0,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides,
  });

  test.beforeEach(async ({ page }) => {
    mockHelper = new MockHelper(page);
    readerPage = new ReaderPage(page);

    // Mock authenticated user
    await mockHelper.mockUser({ id: mockUser.id, nickname: mockUser.nickname });

    // Mock Novel (ID 1)
    await mockHelper.mockNovel(1, {
      title: 'Comment Novel',
      allow_branching: true,
    });

    // Mock Chapter with paragraph-specific content
    await mockHelper.mockChapter(10, {
      id: 10,
      chapter_number: 1,
      title: 'Chapter 1',
      content_html: `<p data-paragraph-index="0">Once upon a time in a land far away, there lived a brave hero.</p>
        <p data-paragraph-index="1">The hero embarked on an epic journey to save the kingdom.</p>`,
    });
  });

  // TODO(#240): Blocked - Paragraph-level comment UI not implemented
  // Waiting on: ParagraphCommentModal component
  // Tracking: https://github.com/hueyjeong/ForkLore/issues/240
  test.fixme('Create paragraph comment', async ({ page }) => {
    // Mock empty comments list initially
    await mockHelper.mockCommentList(10, []);

    // Mock comment creation endpoint
    const newComment = createMockComment({
      id: 100,
      content: 'Great opening paragraph!',
      paragraph_index: 0,
      quoted_text: 'Once upon a time in a land far away',
    });

    await mockHelper.mockCreateComment(10, newComment);

    // Mock updated comments list after creation
    await mockHelper.mockCommentList(10, [newComment]);

    // Navigate to Chapter 1
    await readerPage.goto(1, 10);
    await readerPage.expectContent(/Once upon a time/);

    // Select text from first paragraph
    await readerPage.selectText('Once upon a time');

    // Verify comment tooltip/button appears
    // Expected UI: A floating button with "Comment" or similar text/aria-label
    const commentButton = page.getByRole('button', { name: /Comment|댓글/i }).first();
    await expect(commentButton).toBeVisible();

    // Click to open comment dialog
    await commentButton.click();

    // Verify comment dialog opens
    const commentDialog = page.getByRole('dialog');
    await expect(commentDialog).toBeVisible();

    // Verify quoted text is displayed
    await expect(commentDialog).toContainText('Once upon a time');

    // Type comment
    const textarea = page.getByRole('textbox');
    await textarea.fill('Great opening paragraph!');

    // Submit comment
    const submitButton = page.getByRole('button', { name: /Submit|등록/i });
    await submitButton.click();

    // Verify success message
    await expect(page.getByText(/Comment created|댓글이 등록되었습니다/)).toBeVisible();

    // Verify comment appears in list
    await expect(page.getByText('Great opening paragraph!')).toBeVisible();
  });

  // TODO(#240): Blocked - Paragraph-level comment UI not implemented
  // Waiting on: ParagraphCommentModal component
  // Tracking: https://github.com/hueyjeong/ForkLore/issues/240
  test.fixme('Like a paragraph comment', async ({ page }) => {
    // Mock existing comment
    const existingComment = createMockComment({
      id: 50,
      content: 'Interesting paragraph!',
      like_count: 3,
    });

    await mockHelper.mockCommentList(10, [existingComment]);

    // Mock like toggle response
    await mockHelper.mockLikeComment(50, { liked: true, like_count: 4 });

    // Navigate to Chapter 1
    await readerPage.goto(1, 10);

    // Locate comment
    const comment = page.getByText('Interesting paragraph!');

    // Verify initial like count
    await expect(page.getByText(/3/)).toBeVisible();

    // Click like button
    const likeButton = comment.locator('..').getByRole('button', { name: /Like|좋아요/i });
    await likeButton.click();

    // Verify like count increased to 4
    await expect(page.getByText(/4/)).toBeVisible();

    // Verify like button is active (filled heart)
    await expect(likeButton.locator('.fill-current')).toBeVisible();
  });

  // TODO(#240): Blocked - Paragraph-level comment UI not implemented
  // Waiting on: ParagraphCommentModal component
  // Tracking: https://github.com/hueyjeong/ForkLore/issues/240
  test.fixme('Delete own paragraph comment', async ({ page }) => {
    // Mock comment by current user
    const userComment = createMockComment({
      id: 99,
      content: 'My comment to delete',
    });

    await mockHelper.mockCommentList(10, [userComment]);

    // Mock delete endpoint
    await mockHelper.mockDeleteComment(99);

    // Navigate to Chapter 1
    await readerPage.goto(1, 10);

    // Verify comment exists
    await expect(page.getByText('My comment to delete')).toBeVisible();

    // Find and click delete button (only visible for own comments)
    const comment = page.getByText('My comment to delete');
    const deleteButton = comment.locator('..').getByRole('button', { name: /Delete|삭제/i });
    await expect(deleteButton).toBeVisible();

    await deleteButton.click();

    // Verify confirmation dialog (if exists) or direct delete
    const confirmButton = page.getByRole('button', { name: /Confirm|확인/i });
    if (await confirmButton.isVisible()) {
      await confirmButton.click();
    }

    // Verify success message
    await expect(page.getByText(/Comment deleted|댓글이 삭제되었습니다/)).toBeVisible();

    // Verify comment removed from list
    await expect(page.getByText('My comment to delete')).not.toBeVisible();

    // Verify empty state
    await expect(page.getByText(/No comments|댓글이 없습니다/)).toBeVisible();
  });

  // TODO(#240): Blocked - Comment UI not integrated into ReaderView component
  // Waiting on: CommentThread component integration in reader page
  // Tracking: https://github.com/hueyjeong/ForkLore/issues/240
  test.fixme('List comments for chapter', async ({ page }) => {
    // Mock multiple comments
    const comments = [
      createMockComment({
        id: 1,
        content: 'First comment',
        user: { id: 2, nickname: 'UserA', profile_image: null },
        created_at: new Date(Date.now() - 3600000).toISOString(),
      }),
      createMockComment({
        id: 2,
        content: 'Second comment',
        user: { id: 3, nickname: 'UserB', profile_image: null },
        created_at: new Date(Date.now() - 1800000).toISOString(),
      }),
    ];

    await mockHelper.mockCommentList(10, comments);

    // Navigate to Chapter 1
    await readerPage.goto(1, 10);

    // Verify comments are displayed
    await expect(page.getByText('First comment')).toBeVisible();
    await expect(page.getByText('Second comment')).toBeVisible();
    await expect(page.getByText('UserA')).toBeVisible();
    await expect(page.getByText('UserB')).toBeVisible();
  });
});

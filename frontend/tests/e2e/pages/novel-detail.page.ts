import { Page, Locator, expect } from '@playwright/test';

export class NovelDetailPage {
  readonly title: Locator;
  readonly author: Locator;
  readonly readButton: Locator;
  readonly chaptersTab: Locator;
  readonly chapterList: Locator;
  
  constructor(public readonly page: Page) {
    this.title = page.locator('h1');
    // "by AuthorName" - locating the span inside the paragraph
    this.author = page.locator('p:has-text("by") span');
    this.readButton = page.getByRole('button', { name: /Read (First Chapter|Now)/i }).first();
    this.chaptersTab = page.getByRole('tab', { name: 'Chapters' });
    this.chapterList = page.locator('[role="tabpanel"][data-state="active"] .flex.flex-col');
  }

  async goto(id: string) {
    await this.page.goto(`/novels/${id}`);
  }

  async startReading() {
    await this.readButton.click();
  }

  async openChaptersTab() {
    await this.chaptersTab.click();
  }

  async selectChapter(chapterTitle: string) {
    await this.openChaptersTab();
    await this.page.getByText(chapterTitle, { exact: false }).click();
  }

  async expectNovelInfo(title: string, author: string) {
    await expect(this.title).toHaveText(title);
    await expect(this.author).toHaveText(author);
  }
}

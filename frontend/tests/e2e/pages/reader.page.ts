import { Page, Locator, expect } from '@playwright/test';

export class ReaderPage {
  readonly content: Locator;
  readonly nextButton: Locator;
  readonly prevButton: Locator;
  readonly settingsButton: Locator;
  readonly tocButton: Locator;
  readonly settingsSheet: Locator;
  readonly themeButtons: {
    light: Locator;
    sepia: Locator;
    dark: Locator;
  };
  readonly fontSizeSlider: Locator;

  constructor(public readonly page: Page) {
    this.content = page.locator('article');
    // Using hasText for Prev/Next buttons as they have text content
    this.prevButton = page.getByRole('button', { name: 'Prev' });
    this.nextButton = page.getByRole('button', { name: 'Next' });
    
    // Icons usually have sr-only text or we rely on position/icon class, but here we can try to find by specific aria attributes if available.
    // The code uses lucide-react icons inside buttons.
    // We can target the SVG or if the button has an aria-label (it should!).
    // Assuming shadcn usage, we might need to target by icon class or order.
    // But since I can't see aria-labels in the code snippet provided (they are missing),
    // I will use locators based on the SVG icon class names if possible or position.
    // Actually, looking at the code: <Settings className="h-5 w-5" /> inside a button.
    // I'll use a locator that finds the button containing the svg with specific class.
    
    this.settingsButton = page.locator('button:has(.lucide-settings)');
    this.tocButton = page.locator('button:has(.lucide-menu)');

    this.settingsSheet = page.locator('[role="dialog"]'); // SheetContent
    
    this.themeButtons = {
      light: page.locator('button', { hasText: 'Light' }),
      sepia: page.locator('button', { hasText: 'Sepia' }),
      dark: page.locator('button', { hasText: 'Dark' }),
    };

    this.fontSizeSlider = page.locator('[role="slider"]');
  }

  async goto(novelId: string | number, chapterId: string | number) {
    await this.page.goto(`/novels/${novelId}/reader/${chapterId}`);
  }

  async nextChapter() {
    await this.nextButton.click();
  }

  async prevChapter() {
    await this.prevButton.click();
  }

  async openSettings() {
    await this.settingsButton.click();
  }

  async setTheme(theme: 'light' | 'sepia' | 'dark') {
    await this.openSettings();
    await this.themeButtons[theme].click();
    // Close sheet logic if needed, usually clicking backdrop or close button
    // page.keyboard.press('Escape');
  }

  async expectContent(text: string | RegExp) {
    await expect(this.content).toContainText(text);
  }
}

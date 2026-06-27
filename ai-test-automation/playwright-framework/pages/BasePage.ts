import { Page, Locator, expect } from '@playwright/test';

export class BasePage {
  protected page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async navigateTo(url: string): Promise<void> {
    await this.page.goto(url, { waitUntil: 'networkidle' });
  }

  async getElement(selector: string): Promise<Locator> {
    return this.page.locator(selector);
  }

  async click(selector: string): Promise<void> {
    const element = await this.getElement(selector);
    await element.waitFor({ state: 'visible' });
    await element.click();
  }

  async fill(selector: string, text: string): Promise<void> {
    const element = await this.getElement(selector);
    await element.waitFor({ state: 'visible' });
    await element.clear();
    await element.fill(text);
  }

  async getText(selector: string): Promise<string> {
    const element = await this.getElement(selector);
    await element.waitFor({ state: 'visible' });
    return element.textContent() || '';
  }

  async isVisible(selector: string): Promise<boolean> {
    try {
      const element = await this.getElement(selector);
      await element.waitFor({ state: 'visible', timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }

  async waitForElement(selector: string, timeout = 10000): Promise<void> {
    const element = await this.getElement(selector);
    await element.waitFor({ state: 'visible', timeout });
  }

  async waitForText(selector: string, text: string, timeout = 10000): Promise<void> {
    const element = await this.getElement(selector);
    await element.waitFor({ state: 'visible', timeout });
    await expect(element).toContainText(text);
  }

  async selectOption(selector: string, value: string): Promise<void> {
    const element = await this.getElement(selector);
    await element.selectOption(value);
  }

  async uploadFile(selector: string, filePath: string): Promise<void> {
    const element = await this.getElement(selector);
    await element.setInputFiles(filePath);
  }

  async pressKey(selector: string, key: string): Promise<void> {
    const element = await this.getElement(selector);
    await element.press(key);
  }

  async takeScreenshot(name: string): Promise<void> {
    await this.page.screenshot({
      path: `./screenshots/${name}-${Date.now()}.png`,
      fullPage: true,
    });
  }

  async waitForNetworkIdle(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  async getPageTitle(): Promise<string> {
    return this.page.title();
  }

  async getCurrentUrl(): Promise<string> {
    return this.page.url();
  }

  async reload(): Promise<void> {
    await this.page.reload({ waitUntil: 'networkidle' });
  }

  async scrollToElement(selector: string): Promise<void> {
    const element = await this.getElement(selector);
    await element.scrollIntoViewIfNeeded();
  }

  async hover(selector: string): Promise<void> {
    const element = await this.getElement(selector);
    await element.hover();
  }

  async doubleClick(selector: string): Promise<void> {
    const element = await this.getElement(selector);
    await element.dblclick();
  }

  async rightClick(selector: string): Promise<void> {
    const element = await this.getElement(selector);
    await element.click({ button: 'right' });
  }

  async dragAndDrop(sourceSelector: string, targetSelector: string): Promise<void> {
    const source = await this.getElement(sourceSelector);
    const target = await this.getElement(targetSelector);
    await source.dragTo(target);
  }

  async waitForTimeout(ms: number): Promise<void> {
    await this.page.waitForTimeout(ms);
  }

  async getAttribute(selector: string, attribute: string): Promise<string | null> {
    const element = await this.getElement(selector);
    return element.getAttribute(attribute);
  }

  async isEnabled(selector: string): Promise<boolean> {
    const element = await this.getElement(selector);
    return element.isEnabled();
  }

  async isChecked(selector: string): Promise<boolean> {
    const element = await this.getElement(selector);
    return element.isChecked();
  }

  async check(selector: string): Promise<void> {
    const element = await this.getElement(selector);
    await element.check();
  }

  async uncheck(selector: string): Promise<void> {
    const element = await this.getElement(selector);
    await element.uncheck();
  }

  async count(selector: string): Promise<number> {
    const element = await this.getElement(selector);
    return element.count();
  }

  async getInnerHtml(selector: string): Promise<string> {
    const element = await this.getElement(selector);
    return element.innerHTML();
  }
}

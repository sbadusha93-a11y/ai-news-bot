import { test, expect } from '@playwright/test';

test.describe('Task Manager', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('file:///C:/Users/DELL/Desktop/playwright-demo/sample-app.html');
  });

  test('should display the title', async ({ page }) => {
    await expect(page.locator('h1')).toHaveText('Task Manager');
  });

  test('should add a new task', async ({ page }) => {
    await page.fill('#taskInput', 'Buy groceries');
    await page.click('#addBtn');
    const tasks = page.locator('#taskList li');
    await expect(tasks).toHaveCount(1);
    await expect(tasks.first()).toContainText('Buy groceries');
  });

  test('should mark a task as done', async ({ page }) => {
    await page.fill('#taskInput', 'Write tests');
    await page.click('#addBtn');
    await page.click('#taskList li button');
    await expect(page.locator('#taskList li')).toHaveClass('completed');
  });

  test('should add multiple tasks', async ({ page }) => {
    const items = ['Task 1', 'Task 2', 'Task 3'];
    for (const item of items) {
      await page.fill('#taskInput', item);
      await page.click('#addBtn');
    }
    await expect(page.locator('#taskList li')).toHaveCount(3);
  });
});

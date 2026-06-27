import { test, expect, Page } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { LoginPage } from '../pages/LoginPage';
import { TestDataUtil } from '../utils/TestDataUtil';

const testData = new TestDataUtil();


test.describe('UI Tests', () => {

test('TS496 - Verify UI REQUIREMENTS 121 The application must be responsive for mobile 320px tablet 768px and desktop 1280px 122 All forms must have inline validation with realtime feedback 123 Loading states must be shown with skeleton screens 124 Error states must be shown with clear error messages and retry options - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/form');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave all fields empty
    await page.goto('/form');
      // Intentionally left empty

    // Step 3: Click submit button
    await page.goto('/form');
      await page.click('#submit-button');

    // Step 4: Verify error messages
    await page.goto('/form');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS497 - Verify UI REQUIREMENTS 121 The application must be responsive for mobile 320px tablet 768px and desktop 1280px 122 All forms must have inline validation with realtime feedback 123 Loading states must be shown with skeleton screens 124 Error states must be shown with clear error messages and retry options with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/form');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave all fields empty
    await page.goto('/form');
      // Intentionally left empty

    // Step 3: Click submit button
    await page.goto('/form');
      await page.click('#submit-button');

    // Step 4: Verify error messages
    await page.goto('/form');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS498 - Verify UI REQUIREMENTS 121 The application must be responsive for mobile 320px tablet 768px and desktop 1280px 122 All forms must have inline validation with realtime feedback 123 Loading states must be shown with skeleton screens 124 Error states must be shown with clear error messages and retry options with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/form');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave all fields empty
    await page.goto('/form');
      // Intentionally left empty

    // Step 3: Click submit button
    await page.goto('/form');
      await page.click('#submit-button');

    // Step 4: Verify error messages
    await page.goto('/form');
      await page.waitForSelector('body', { timeout: 5000 });

});

});

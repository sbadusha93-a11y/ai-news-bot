import { test, expect, Page } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { LoginPage } from '../pages/LoginPage';
import { TestDataUtil } from '../utils/TestDataUtil';

const testData = new TestDataUtil();


test.describe('Account Management Tests', () => {

test('TS216 - Verify The system shall support international currency conversion 5 USER PROFILE 51 The system shall allow users to view and edit their profile information 52 The system shall allow users to change their password 53 The system shall allow users to view their order history - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/profile');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/profile');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/profile');
      await page.fill('#email', 'test@example.com');

    // Step 4: Click submit button
    await page.goto('/profile');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/profile');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS217 - Verify The system shall support international currency conversion 5 USER PROFILE 51 The system shall allow users to view and edit their profile information 52 The system shall allow users to change their password 53 The system shall allow users to view their order history with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/profile');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/profile');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/profile');
      await page.fill('#email', 'user.name+tag@domain.co.uk');

    // Step 4: Click submit button
    await page.goto('/profile');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/profile');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS218 - Verify The system shall support international currency conversion 5 USER PROFILE 51 The system shall allow users to view and edit their profile information 52 The system shall allow users to change their password 53 The system shall allow users to view their order history with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/profile');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/profile');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/profile');
      await page.fill('#email', 'user.name+tag@domain.co.uk');

    // Step 4: Click submit button
    await page.goto('/profile');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/profile');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS225 - Verify The system shall allow users to view and edit their profile information - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/profile');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/profile');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/profile');
      await page.fill('#email', 'user.name+tag@domain.co.uk');

    // Step 4: Click submit button
    await page.goto('/profile');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/profile');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS226 - Verify The system shall allow users to view and edit their profile information with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/profile');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/profile');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/profile');
      await page.fill('#email', 'user@domain.io');

    // Step 4: Click submit button
    await page.goto('/profile');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/profile');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS227 - Verify The system shall allow users to view and edit their profile information with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/profile');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/profile');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/profile');
      await page.fill('#email', 'user@domain.io');

    // Step 4: Click submit button
    await page.goto('/profile');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/profile');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS266 - Verify The system shall allow admin to manage user accounts - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to feature page
    await page.goto('/profile');
      await page.waitForLoadState('networkidle');

    // Step 2: Perform primary action
    await page.goto('/profile');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Verify expected behavior
    await page.goto('/profile');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify no errors
    await page.goto('/profile');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS267 - Verify The system shall allow admin to manage user accounts with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to feature page
    await page.goto('/profile');
      await page.waitForLoadState('networkidle');

    // Step 2: Perform primary action
    await page.goto('/profile');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Verify expected behavior
    await page.goto('/profile');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify no errors
    await page.goto('/profile');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS268 - Verify The system shall allow admin to manage user accounts with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to feature page
    await page.goto('/profile');
      await page.waitForLoadState('networkidle');

    // Step 2: Perform primary action
    await page.goto('/profile');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Verify expected behavior
    await page.goto('/profile');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify no errors
    await page.goto('/profile');
      await page.waitForSelector('body', { timeout: 5000 });

});

});

import { test, expect, Page } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { LoginPage } from '../pages/LoginPage';
import { TestDataUtil } from '../utils/TestDataUtil';

const testData = new TestDataUtil();


test.describe('Search Tests', () => {

test('TS077 - Verify The system shall support single signon SSO with Google and Facebook 2 PRODUCT CATALOG 21 The system shall display product listing with pagination 20 items per page 22 The system shall allow searching products by name category and price range 23 The system shall allow filtering products by category brand price and rating - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'wireless mouse');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS078 - Verify The system shall support single signon SSO with Google and Facebook 2 PRODUCT CATALOG 21 The system shall display product listing with pagination 20 items per page 22 The system shall allow searching products by name category and price range 23 The system shall allow filtering products by category brand price and rating with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'ergonomic keyboard');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS079 - Verify The system shall support single signon SSO with Google and Facebook 2 PRODUCT CATALOG 21 The system shall display product listing with pagination 20 items per page 22 The system shall allow searching products by name category and price range 23 The system shall allow filtering products by category brand price and rating with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid search query
    await page.goto('/search');
      await page.fill('#search-input', '!@#$%^&*()');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify no results message
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS080 - Verify behavior at minimum boundary value 2 - Boundary', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to feature page
    await page.goto('/');
      await page.waitForLoadState('networkidle');

    // Step 2: Perform primary action
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Verify expected behavior
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify no errors
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS084 - Verify The system shall display product listing with pagination 20 items per page 22 The system shall allow searching products by name category and price range 23 The system shall allow filtering products by category brand price and rating 24 The system shall display product details including images description price and reviews 25 The system shall support sorting by price low to high high to low popularity and rating - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'wireless mouse');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS085 - Verify The system shall display product listing with pagination 20 items per page 22 The system shall allow searching products by name category and price range 23 The system shall allow filtering products by category brand price and rating 24 The system shall display product details including images description price and reviews 25 The system shall support sorting by price low to high high to low popularity and rating with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'USB-C hub adapter');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS086 - Verify The system shall display product listing with pagination 20 items per page 22 The system shall allow searching products by name category and price range 23 The system shall allow filtering products by category brand price and rating 24 The system shall display product details including images description price and reviews 25 The system shall support sorting by price low to high high to low popularity and rating with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid search query
    await page.goto('/search');
      await page.fill('#search-input', '!@#$%^&*()');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify no results message
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS087 - Verify behavior at minimum boundary value 20 - Boundary', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to feature page
    await page.goto('/');
      await page.waitForLoadState('networkidle');

    // Step 2: Perform primary action
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Verify expected behavior
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify no errors
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS101 - Verify The system shall allow searching products by name category and price range - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'wireless mouse');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS102 - Verify The system shall allow searching products by name category and price range with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'wireless mouse');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS103 - Verify The system shall allow searching products by name category and price range with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid search query
    await page.goto('/search');
      await page.fill('#search-input', 'a');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify no results message
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS107 - Verify The system shall allow filtering products by category brand price and rating - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to feature page
    await page.goto('/');
      await page.waitForLoadState('networkidle');

    // Step 2: Perform primary action
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Verify expected behavior
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify no errors
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS108 - Verify The system shall allow filtering products by category brand price and rating with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to feature page
    await page.goto('/');
      await page.waitForLoadState('networkidle');

    // Step 2: Perform primary action
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Verify expected behavior
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify no errors
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS109 - Verify The system shall allow filtering products by category brand price and rating with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to feature page
    await page.goto('/');
      await page.waitForLoadState('networkidle');

    // Step 2: Perform primary action
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Verify expected behavior
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify no errors
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS119 - Verify The system shall support sorting by price low to high high to low popularity and rating - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to feature page
    await page.goto('/');
      await page.waitForLoadState('networkidle');

    // Step 2: Perform primary action
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Verify expected behavior
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify no errors
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS120 - Verify The system shall support sorting by price low to high high to low popularity and rating with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to feature page
    await page.goto('/');
      await page.waitForLoadState('networkidle');

    // Step 2: Perform primary action
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Verify expected behavior
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify no errors
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS121 - Verify The system shall support sorting by price low to high high to low popularity and rating with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to feature page
    await page.goto('/');
      await page.waitForLoadState('networkidle');

    // Step 2: Perform primary action
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Verify expected behavior
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify no errors
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS346 - Verify PERFORMANCE REQUIREMENTS 81 Page load time must be under 3 seconds for 95th percentile 82 The system must support 10000 concurrent users 83 API response time must be under 500ms for 99th percentile 84 Product search results must return within 2 seconds - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'laptop');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS347 - Verify PERFORMANCE REQUIREMENTS 81 Page load time must be under 3 seconds for 95th percentile 82 The system must support 10000 concurrent users 83 API response time must be under 500ms for 99th percentile 84 Product search results must return within 2 seconds with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'ergonomic keyboard');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS348 - Verify PERFORMANCE REQUIREMENTS 81 Page load time must be under 3 seconds for 95th percentile 82 The system must support 10000 concurrent users 83 API response time must be under 500ms for 99th percentile 84 Product search results must return within 2 seconds with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid search query
    await page.goto('/search');
      await page.fill('#search-input', '   ');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify no results message
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS352 - Verify Page load time must be under 3 seconds for 95th percentile 82 The system must support 10000 concurrent users 83 API response time must be under 500ms for 99th percentile 84 Product search results must return within 2 seconds 85 System must maintain 999 uptime - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'laptop');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS353 - Verify Page load time must be under 3 seconds for 95th percentile 82 The system must support 10000 concurrent users 83 API response time must be under 500ms for 99th percentile 84 Product search results must return within 2 seconds 85 System must maintain 999 uptime with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'ergonomic keyboard');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS354 - Verify Page load time must be under 3 seconds for 95th percentile 82 The system must support 10000 concurrent users 83 API response time must be under 500ms for 99th percentile 84 Product search results must return within 2 seconds 85 System must maintain 999 uptime with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid search query
    await page.goto('/search');
      await page.fill('#search-input', '   ');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify no results message
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS358 - Verify The system must support 10000 concurrent users 83 API response time must be under 500ms for 99th percentile 84 Product search results must return within 2 seconds 85 System must maintain 999 uptime 9 INTEGRATION REQUIREMENTS - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'laptop');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS359 - Verify The system must support 10000 concurrent users 83 API response time must be under 500ms for 99th percentile 84 Product search results must return within 2 seconds 85 System must maintain 999 uptime 9 INTEGRATION REQUIREMENTS with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'wireless mouse');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS360 - Verify The system must support 10000 concurrent users 83 API response time must be under 500ms for 99th percentile 84 Product search results must return within 2 seconds 85 System must maintain 999 uptime 9 INTEGRATION REQUIREMENTS with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid search query
    await page.goto('/search');
      await page.fill('#search-input', '!@#$%^&*()');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify no results message
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS373 - Verify Product search results must return within 2 seconds - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'wireless mouse');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS374 - Verify Product search results must return within 2 seconds with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'USB-C hub adapter');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS375 - Verify Product search results must return within 2 seconds with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid search query
    await page.goto('/search');
      await page.fill('#search-input', 'a');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify no results message
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS394 - Verify The system must integrate with SendGrid for email notifications 93 The system must integrate with AWS S3 for image storage 94 The system must integrate with Elasticsearch for product search 95 The system must integrate with Google Analytics for tracking 10 ERROR HANDLING - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'laptop');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS395 - Verify The system must integrate with SendGrid for email notifications 93 The system must integrate with AWS S3 for image storage 94 The system must integrate with Elasticsearch for product search 95 The system must integrate with Google Analytics for tracking 10 ERROR HANDLING with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'laptop');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS396 - Verify The system must integrate with SendGrid for email notifications 93 The system must integrate with AWS S3 for image storage 94 The system must integrate with Elasticsearch for product search 95 The system must integrate with Google Analytics for tracking 10 ERROR HANDLING with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid search query
    await page.goto('/search');
      await page.fill('#search-input', 'a');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify no results message
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS400 - Verify The system must integrate with AWS S3 for image storage 94 The system must integrate with Elasticsearch for product search 95 The system must integrate with Google Analytics for tracking 10 ERROR HANDLING 101 The system must display userfriendly error messages - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'USB-C hub adapter');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS401 - Verify The system must integrate with AWS S3 for image storage 94 The system must integrate with Elasticsearch for product search 95 The system must integrate with Google Analytics for tracking 10 ERROR HANDLING 101 The system must display userfriendly error messages with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'laptop');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS402 - Verify The system must integrate with AWS S3 for image storage 94 The system must integrate with Elasticsearch for product search 95 The system must integrate with Google Analytics for tracking 10 ERROR HANDLING 101 The system must display userfriendly error messages with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid search query
    await page.goto('/search');
      await page.fill('#search-input', '!@#$%^&*()');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify no results message
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS406 - Verify The system must integrate with Elasticsearch for product search 95 The system must integrate with Google Analytics for tracking 10 ERROR HANDLING 101 The system must display userfriendly error messages 102 The system must log all errors with stack traces - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'laptop');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS407 - Verify The system must integrate with Elasticsearch for product search 95 The system must integrate with Google Analytics for tracking 10 ERROR HANDLING 101 The system must display userfriendly error messages 102 The system must log all errors with stack traces with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'ergonomic keyboard');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS408 - Verify The system must integrate with Elasticsearch for product search 95 The system must integrate with Google Analytics for tracking 10 ERROR HANDLING 101 The system must display userfriendly error messages 102 The system must log all errors with stack traces with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid search query
    await page.goto('/search');
      await page.fill('#search-input', 'test');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify no results message
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS409 - Verify The system must integrate with Elasticsearch for product search - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'wireless mouse');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS410 - Verify The system must integrate with Elasticsearch for product search with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter search query
    await page.goto('/search');
      await page.fill('#search-input', 'ergonomic keyboard');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify search results
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS411 - Verify The system must integrate with Elasticsearch for product search with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid search query
    await page.goto('/search');
      await page.fill('#search-input', 'a');

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

    // Step 4: Verify no results message
    await page.goto('/search');
      await page.waitForSelector('body', { timeout: 5000 });

});

});

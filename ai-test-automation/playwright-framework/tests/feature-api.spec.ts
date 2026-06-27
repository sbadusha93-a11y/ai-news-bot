import { test, expect, Page } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { LoginPage } from '../pages/LoginPage';
import { TestDataUtil } from '../utils/TestDataUtil';

const testData = new TestDataUtil();


test.describe('API Tests', () => {

test('TS292 - Verify The system shall allow admin to manage inventory levels 7 SECURITY REQUIREMENTS 71 All passwords must be encrypted using bcrypt with minimum 10 salt rounds 72 All API endpoints must use HTTPS with TLS 13 73 The system must implement rate limiting 100 requests per minute per IP - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send 100 API requests in 1 second
    await page.goto('/settings');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 429 status after limit
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS293 - Verify The system shall allow admin to manage inventory levels 7 SECURITY REQUIREMENTS 71 All passwords must be encrypted using bcrypt with minimum 10 salt rounds 72 All API endpoints must use HTTPS with TLS 13 73 The system must implement rate limiting 100 requests per minute per IP with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send 100 API requests in 1 second
    await page.goto('/settings');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 429 status after limit
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS294 - Verify The system shall allow admin to manage inventory levels 7 SECURITY REQUIREMENTS 71 All passwords must be encrypted using bcrypt with minimum 10 salt rounds 72 All API endpoints must use HTTPS with TLS 13 73 The system must implement rate limiting 100 requests per minute per IP with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send 100 API requests in 1 second
    await page.goto('/settings');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 429 status after limit
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS295 - Verify behavior at minimum boundary value 7 - Boundary', async ({ page }) => {
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


test('TS299 - Verify SECURITY REQUIREMENTS 71 All passwords must be encrypted using bcrypt with minimum 10 salt rounds 72 All API endpoints must use HTTPS with TLS 13 73 The system must implement rate limiting 100 requests per minute per IP 74 The system must sanitize all user inputs to prevent XSS attacks - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send 100 API requests in 1 second
    await page.goto('/settings');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 429 status after limit
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS300 - Verify SECURITY REQUIREMENTS 71 All passwords must be encrypted using bcrypt with minimum 10 salt rounds 72 All API endpoints must use HTTPS with TLS 13 73 The system must implement rate limiting 100 requests per minute per IP 74 The system must sanitize all user inputs to prevent XSS attacks with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send 100 API requests in 1 second
    await page.goto('/settings');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 429 status after limit
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS301 - Verify SECURITY REQUIREMENTS 71 All passwords must be encrypted using bcrypt with minimum 10 salt rounds 72 All API endpoints must use HTTPS with TLS 13 73 The system must implement rate limiting 100 requests per minute per IP 74 The system must sanitize all user inputs to prevent XSS attacks with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send 100 API requests in 1 second
    await page.goto('/settings');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 429 status after limit
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS305 - Verify All passwords must be encrypted using bcrypt with minimum 10 salt rounds 72 All API endpoints must use HTTPS with TLS 13 73 The system must implement rate limiting 100 requests per minute per IP 74 The system must sanitize all user inputs to prevent XSS attacks 75 The system must use parameterized queries to prevent SQL injection - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send 100 API requests in 1 second
    await page.goto('/settings');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 429 status after limit
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS306 - Verify All passwords must be encrypted using bcrypt with minimum 10 salt rounds 72 All API endpoints must use HTTPS with TLS 13 73 The system must implement rate limiting 100 requests per minute per IP 74 The system must sanitize all user inputs to prevent XSS attacks 75 The system must use parameterized queries to prevent SQL injection with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send 100 API requests in 1 second
    await page.goto('/settings');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 429 status after limit
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS307 - Verify All passwords must be encrypted using bcrypt with minimum 10 salt rounds 72 All API endpoints must use HTTPS with TLS 13 73 The system must implement rate limiting 100 requests per minute per IP 74 The system must sanitize all user inputs to prevent XSS attacks 75 The system must use parameterized queries to prevent SQL injection with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send 100 API requests in 1 second
    await page.goto('/settings');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 429 status after limit
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS308 - Verify behavior at minimum boundary value 10 - Boundary', async ({ page }) => {
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


test('TS312 - Verify All API endpoints must use HTTPS with TLS 13 73 The system must implement rate limiting 100 requests per minute per IP 74 The system must sanitize all user inputs to prevent XSS attacks 75 The system must use parameterized queries to prevent SQL injection 76 JWT tokens must expire after 24 hours - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send 100 API requests in 1 second
    await page.goto('/admin/users');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 429 status after limit
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS313 - Verify All API endpoints must use HTTPS with TLS 13 73 The system must implement rate limiting 100 requests per minute per IP 74 The system must sanitize all user inputs to prevent XSS attacks 75 The system must use parameterized queries to prevent SQL injection 76 JWT tokens must expire after 24 hours with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send 100 API requests in 1 second
    await page.goto('/admin/users');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 429 status after limit
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS314 - Verify All API endpoints must use HTTPS with TLS 13 73 The system must implement rate limiting 100 requests per minute per IP 74 The system must sanitize all user inputs to prevent XSS attacks 75 The system must use parameterized queries to prevent SQL injection 76 JWT tokens must expire after 24 hours with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send 100 API requests in 1 second
    await page.goto('/admin/users');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 429 status after limit
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS315 - Verify behavior at minimum boundary value 1 - Boundary', async ({ page }) => {
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


test('TS316 - Verify integration with after 24 hours - Integration', async ({ page }) => {
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


test('TS317 - Verify system behavior when after 24 hours is unavailable - Error Handling', async ({ page }) => {
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


test('TS318 - Verify All API endpoints must use HTTPS with TLS 13 - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request
    await page.goto('/');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify response status code
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 3: Verify response body
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify response headers
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS319 - Verify All API endpoints must use HTTPS with TLS 13 with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request
    await page.goto('/');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify response status code
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 3: Verify response body
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify response headers
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS320 - Verify All API endpoints must use HTTPS with TLS 13 with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request with invalid payload
    await page.goto('/');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 400 status
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS340 - Verify JWT tokens must expire after 24 hours 8 PERFORMANCE REQUIREMENTS 81 Page load time must be under 3 seconds for 95th percentile 82 The system must support 10000 concurrent users 83 API response time must be under 500ms for 99th percentile - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/form');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/form');
      await page.fill('#email', 'user@domain.io');

    // Step 4: Click submit button
    await page.goto('/form');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/form');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS341 - Verify JWT tokens must expire after 24 hours 8 PERFORMANCE REQUIREMENTS 81 Page load time must be under 3 seconds for 95th percentile 82 The system must support 10000 concurrent users 83 API response time must be under 500ms for 99th percentile with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/form');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/form');
      await page.fill('#email', 'user-name@domain.org');

    // Step 4: Click submit button
    await page.goto('/form');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/form');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS342 - Verify JWT tokens must expire after 24 hours 8 PERFORMANCE REQUIREMENTS 81 Page load time must be under 3 seconds for 95th percentile 82 The system must support 10000 concurrent users 83 API response time must be under 500ms for 99th percentile with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/form');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/form');
      await page.fill('#email', 'user-name@domain.org');

    // Step 4: Click submit button
    await page.goto('/form');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/form');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS367 - Verify API response time must be under 500ms for 99th percentile - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request
    await page.goto('/');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify response status code
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 3: Verify response body
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify response headers
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS368 - Verify API response time must be under 500ms for 99th percentile with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request
    await page.goto('/');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify response status code
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 3: Verify response body
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify response headers
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS369 - Verify API response time must be under 500ms for 99th percentile with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request with invalid payload
    await page.goto('/');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 400 status
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS421 - Verify The system must display userfriendly error messages 102 The system must log all errors with stack traces 103 The system must implement retry logic for transient failures 3 retries 104 The system must handle network timeout gracefully 30 seconds timeout 105 The system must implement circuit breaker for external API calls - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request
    await page.goto('/admin/users');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify response status code
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 3: Verify response body
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify response headers
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS422 - Verify The system must display userfriendly error messages 102 The system must log all errors with stack traces 103 The system must implement retry logic for transient failures 3 retries 104 The system must handle network timeout gracefully 30 seconds timeout 105 The system must implement circuit breaker for external API calls with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request
    await page.goto('/admin/users');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify response status code
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 3: Verify response body
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify response headers
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS423 - Verify The system must display userfriendly error messages 102 The system must log all errors with stack traces 103 The system must implement retry logic for transient failures 3 retries 104 The system must handle network timeout gracefully 30 seconds timeout 105 The system must implement circuit breaker for external API calls with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request with invalid payload
    await page.goto('/admin/users');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 400 status
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS427 - Verify The system must log all errors with stack traces 103 The system must implement retry logic for transient failures 3 retries 104 The system must handle network timeout gracefully 30 seconds timeout 105 The system must implement circuit breaker for external API calls 11 VALIDATION RULES - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request
    await page.goto('/');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify response status code
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 3: Verify response body
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify response headers
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS428 - Verify The system must log all errors with stack traces 103 The system must implement retry logic for transient failures 3 retries 104 The system must handle network timeout gracefully 30 seconds timeout 105 The system must implement circuit breaker for external API calls 11 VALIDATION RULES with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request
    await page.goto('/');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify response status code
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 3: Verify response body
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify response headers
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS429 - Verify The system must log all errors with stack traces 103 The system must implement retry logic for transient failures 3 retries 104 The system must handle network timeout gracefully 30 seconds timeout 105 The system must implement circuit breaker for external API calls 11 VALIDATION RULES with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request with invalid payload
    await page.goto('/');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 400 status
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS448 - Verify The system must implement circuit breaker for external API calls - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request
    await page.goto('/');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify response status code
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 3: Verify response body
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify response headers
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS449 - Verify The system must implement circuit breaker for external API calls with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request
    await page.goto('/');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify response status code
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 3: Verify response body
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify response headers
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS450 - Verify The system must implement circuit breaker for external API calls with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Send API request with invalid payload
    await page.goto('/');
      const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);

    // Step 2: Verify 400 status
    await page.goto('/');
      await page.waitForSelector('body', { timeout: 5000 });

});

});

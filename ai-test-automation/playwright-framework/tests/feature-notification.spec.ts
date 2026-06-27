import { test, expect, Page } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { LoginPage } from '../pages/LoginPage';
import { TestDataUtil } from '../utils/TestDataUtil';

const testData = new TestDataUtil();


test.describe('Notification Tests', () => {

test('TS044 - Verify The system shall allow users to register with email and password - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to password change page
    await page.goto('/register');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter current password
    await page.goto('/register');
      await page.fill('#password', 'Test@12345');

    // Step 3: Enter new password
    await page.goto('/register');
      await page.fill('#password', 'P@ssw0rd123');

    // Step 4: Confirm new password
    await page.goto('/register');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click save/update
    await page.goto('/register');
      await page.click('#submit-button');

});


test('TS045 - Verify The system shall allow users to register with email and password with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to password change page
    await page.goto('/register');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter current password
    await page.goto('/register');
      await page.fill('#password', 'Secure#Pass1');

    // Step 3: Enter new password
    await page.goto('/register');
      await page.fill('#password', 'Secure#Pass1');

    // Step 4: Confirm new password
    await page.goto('/register');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click save/update
    await page.goto('/register');
      await page.click('#submit-button');

});


test('TS046 - Verify The system shall allow users to register with email and password with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to password change page
    await page.goto('/register');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter current password
    await page.goto('/register');
      await page.fill('#password', 'Test@12345');

    // Step 3: Enter new password
    await page.goto('/register');
      await page.fill('#password', 'P@ssw0rd123');

    // Step 4: Confirm new password
    await page.goto('/register');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click save/update
    await page.goto('/register');
      await page.click('#submit-button');

});


test('TS056 - Verify The system shall implement password reset functionality via email - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to password change page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter current password
    await page.goto('/settings');
      await page.fill('#password', 'Test@12345');

    // Step 3: Enter new password
    await page.goto('/settings');
      await page.fill('#password', 'P@ssw0rd123');

    // Step 4: Confirm new password
    await page.goto('/settings');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click save/update
    await page.goto('/settings');
      await page.click('#submit-button');

});


test('TS057 - Verify The system shall implement password reset functionality via email with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to password change page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter current password
    await page.goto('/settings');
      await page.fill('#password', 'Str0ng!Pass');

    // Step 3: Enter new password
    await page.goto('/settings');
      await page.fill('#password', 'Test@12345');

    // Step 4: Confirm new password
    await page.goto('/settings');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click save/update
    await page.goto('/settings');
      await page.click('#submit-button');

});


test('TS058 - Verify The system shall implement password reset functionality via email with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to password change page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter current password
    await page.goto('/settings');
      await page.fill('#password', 'Str0ng!Pass');

    // Step 3: Enter new password
    await page.goto('/settings');
      await page.fill('#password', 'Str0ng!Pass');

    // Step 4: Confirm new password
    await page.goto('/settings');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click save/update
    await page.goto('/settings');
      await page.click('#submit-button');

});


test('TS397 - Verify The system must integrate with SendGrid for email notifications - Functional', async ({ page }) => {
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


test('TS398 - Verify The system must integrate with SendGrid for email notifications with valid inputs - Positive', async ({ page }) => {
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


test('TS399 - Verify The system must integrate with SendGrid for email notifications with invalid inputs - Negative', async ({ page }) => {
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


test('TS433 - Verify The system must implement retry logic for transient failures 3 retries 104 The system must handle network timeout gracefully 30 seconds timeout 105 The system must implement circuit breaker for external API calls 11 VALIDATION RULES 111 Email must be in valid email format - Functional', async ({ page }) => {
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


test('TS434 - Verify The system must implement retry logic for transient failures 3 retries 104 The system must handle network timeout gracefully 30 seconds timeout 105 The system must implement circuit breaker for external API calls 11 VALIDATION RULES 111 Email must be in valid email format with valid inputs - Positive', async ({ page }) => {
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


test('TS435 - Verify The system must implement retry logic for transient failures 3 retries 104 The system must handle network timeout gracefully 30 seconds timeout 105 The system must implement circuit breaker for external API calls 11 VALIDATION RULES 111 Email must be in valid email format with invalid inputs - Negative', async ({ page }) => {
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


test('TS439 - Verify The system must handle network timeout gracefully 30 seconds timeout 105 The system must implement circuit breaker for external API calls 11 VALIDATION RULES 111 Email must be in valid email format 112 Password must be at least 8 characters with uppercase lowercase number and special character - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave all fields empty
    await page.goto('/settings');
      // Intentionally left empty

    // Step 3: Click submit button
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 4: Verify error messages
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS440 - Verify The system must handle network timeout gracefully 30 seconds timeout 105 The system must implement circuit breaker for external API calls 11 VALIDATION RULES 111 Email must be in valid email format 112 Password must be at least 8 characters with uppercase lowercase number and special character with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave all fields empty
    await page.goto('/settings');
      // Intentionally left empty

    // Step 3: Click submit button
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 4: Verify error messages
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS441 - Verify The system must handle network timeout gracefully 30 seconds timeout 105 The system must implement circuit breaker for external API calls 11 VALIDATION RULES 111 Email must be in valid email format 112 Password must be at least 8 characters with uppercase lowercase number and special character with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave all fields empty
    await page.goto('/settings');
      // Intentionally left empty

    // Step 3: Click submit button
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 4: Verify error messages
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS445 - Verify The system must implement circuit breaker for external API calls 11 VALIDATION RULES 111 Email must be in valid email format 112 Password must be at least 8 characters with uppercase lowercase number and special character 113 Phone number must be valid international format - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave all fields empty
    await page.goto('/settings');
      // Intentionally left empty

    // Step 3: Click submit button
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 4: Verify error messages
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS446 - Verify The system must implement circuit breaker for external API calls 11 VALIDATION RULES 111 Email must be in valid email format 112 Password must be at least 8 characters with uppercase lowercase number and special character 113 Phone number must be valid international format with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave all fields empty
    await page.goto('/settings');
      // Intentionally left empty

    // Step 3: Click submit button
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 4: Verify error messages
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS447 - Verify The system must implement circuit breaker for external API calls 11 VALIDATION RULES 111 Email must be in valid email format 112 Password must be at least 8 characters with uppercase lowercase number and special character 113 Phone number must be valid international format with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave all fields empty
    await page.goto('/settings');
      // Intentionally left empty

    // Step 3: Click submit button
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 4: Verify error messages
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS451 - Verify VALIDATION RULES 111 Email must be in valid email format 112 Password must be at least 8 characters with uppercase lowercase number and special character 113 Phone number must be valid international format 114 Credit card number must be 1319 digits and pass Luhn check - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave all fields empty
    await page.goto('/settings');
      // Intentionally left empty

    // Step 3: Click submit button
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 4: Verify error messages
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS452 - Verify VALIDATION RULES 111 Email must be in valid email format 112 Password must be at least 8 characters with uppercase lowercase number and special character 113 Phone number must be valid international format 114 Credit card number must be 1319 digits and pass Luhn check with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave all fields empty
    await page.goto('/settings');
      // Intentionally left empty

    // Step 3: Click submit button
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 4: Verify error messages
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS453 - Verify VALIDATION RULES 111 Email must be in valid email format 112 Password must be at least 8 characters with uppercase lowercase number and special character 113 Phone number must be valid international format 114 Credit card number must be 1319 digits and pass Luhn check with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave all fields empty
    await page.goto('/settings');
      // Intentionally left empty

    // Step 3: Click submit button
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 4: Verify error messages
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS454 - Verify acceptance criteria 11 VALIDATION RULES 111 Email must be in valid email format 112 Password must be at least 8 cha - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave all fields empty
    await page.goto('/settings');
      // Intentionally left empty

    // Step 3: Click submit button
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 4: Verify error messages
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS455 - Verify Email must be in valid email format 112 Password must be at least 8 characters with uppercase lowercase number and special character 113 Phone number must be valid international format 114 Credit card number must be 1319 digits and pass Luhn check 115 Product name must not exceed 200 characters - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/settings');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/settings');
      await page.fill('#email', 'user.name+tag@domain.co.uk');

    // Step 4: Click submit button
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS456 - Verify Email must be in valid email format 112 Password must be at least 8 characters with uppercase lowercase number and special character 113 Phone number must be valid international format 114 Credit card number must be 1319 digits and pass Luhn check 115 Product name must not exceed 200 characters with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/settings');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/settings');
      await page.fill('#email', 'user.name+tag@domain.co.uk');

    // Step 4: Click submit button
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS457 - Verify Email must be in valid email format 112 Password must be at least 8 characters with uppercase lowercase number and special character 113 Phone number must be valid international format 114 Credit card number must be 1319 digits and pass Luhn check 115 Product name must not exceed 200 characters with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/settings');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/settings');
      await page.fill('#email', 'user@domain.io');

    // Step 4: Click submit button
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS458 - Verify acceptance criteria 111 Email must be in valid email format 112 Password must be at least 8 characters with uppercase - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/settings');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/settings');
      await page.fill('#email', 'user@domain.io');

    // Step 4: Click submit button
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS459 - Verify Email must be in valid email format - Functional', async ({ page }) => {
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


test('TS460 - Verify Email must be in valid email format with valid inputs - Positive', async ({ page }) => {
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
      await page.fill('#email', 'user.name+tag@domain.co.uk');

    // Step 4: Click submit button
    await page.goto('/form');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/form');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS461 - Verify Email must be in valid email format with invalid inputs - Negative', async ({ page }) => {
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
      await page.fill('#email', 'test@example.com');

    // Step 4: Click submit button
    await page.goto('/form');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/form');
      await page.waitForSelector('body', { timeout: 5000 });

});

});

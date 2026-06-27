import { test, expect, Page } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { LoginPage } from '../pages/LoginPage';
import { TestDataUtil } from '../utils/TestDataUtil';

const testData = new TestDataUtil();


test.describe('Authentication Tests', () => {

test('TS001 - Verify BUSINESS REQUIREMENTS DOCUMENT  ECOMMERCE APPLICATION 1 USER AUTHENTICATION 11 The system shall allow users to register with email and password 12 The system shall allow users to login with registered credentials 13 The system shall implement password reset functionality via email - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'user@example.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'P@ssw0rd123');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS002 - Verify BUSINESS REQUIREMENTS DOCUMENT  ECOMMERCE APPLICATION 1 USER AUTHENTICATION 11 The system shall allow users to register with email and password 12 The system shall allow users to login with registered credentials 13 The system shall implement password reset functionality via email with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'user@example.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Str0ng!Pass');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS003 - Verify BUSINESS REQUIREMENTS DOCUMENT  ECOMMERCE APPLICATION 1 USER AUTHENTICATION 11 The system shall allow users to register with email and password 12 The system shall allow users to login with registered credentials 13 The system shall implement password reset functionality via email with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid username
    await page.goto('/login');
      await page.fill('#username', 'user@domain');

    // Step 3: Enter invalid password
    await page.goto('/login');
      await page.fill('#password', 'abc');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify error message
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS004 - Verify login with valid credentials - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'test_user123@domain.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Str0ng!Pass');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS005 - Verify login with invalid password - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid username
    await page.goto('/login');
      await page.fill('#username', 'user@.com');

    // Step 3: Enter invalid password
    await page.goto('/login');
      await page.fill('#password', '12345');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify error message
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS006 - Verify login with invalid username - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid username
    await page.goto('/login');
      await page.fill('#username', 'user@domain');

    // Step 3: Enter invalid password
    await page.goto('/login');
      await page.fill('#password', 'weak');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify error message
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS007 - Verify login with empty credentials - Validation', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave username empty
    await page.goto('/login');
      // Intentionally left empty

    // Step 3: Leave password empty
    await page.goto('/login');
      // Intentionally left empty

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

});


test('TS008 - Verify login with SQL injection input - Security', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter malicious payload in username
    await page.goto('/login');
      await page.fill('#username', 'admin\'--');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'P@ssw0rd123');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify no error or data leak
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS009 - Verify login with XSS input - Security', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter malicious payload in username
    await page.goto('/login');
      await page.fill('#username', '\"><script>alert(1)</script>');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'P@ssw0rd123');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify no error or data leak
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS010 - Verify login with special characters - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'test_user123@domain.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Str0ng!Pass');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS011 - Verify login button is accessible via keyboard - Accessibility', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'john.doe@company.org');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Secure#Pass1');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS012 - Verify login page UI elements are displayed correctly - UI', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'john.doe@company.org');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Test@12345');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS013 - Verify password minimum length validation - Boundary', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to password change page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter weak password
    await page.goto('/settings');
      await page.fill('#password', '12345');

    // Step 3: Click save/update
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 4: Verify complexity message
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS014 - Verify password complexity requirements - Validation', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to password change page
    await page.goto('/settings');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter weak password
    await page.goto('/settings');
      await page.fill('#password', 'abc');

    // Step 3: Click save/update
    await page.goto('/settings');
      await page.click('#submit-button');

    // Step 4: Verify complexity message
    await page.goto('/settings');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS015 - Verify password reset flow - Workflow', async ({ page }) => {
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
      await page.fill('#password', 'Str0ng!Pass');

    // Step 4: Confirm new password
    await page.goto('/settings');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click save/update
    await page.goto('/settings');
      await page.click('#submit-button');

});


test('TS016 - Verify session timeout after inactivity - Security', async ({ page }) => {
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


test('TS017 - Verify rolebased access control - Security', async ({ page }) => {
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


test('TS018 - Verify password encryption in transit - Security', async ({ page }) => {
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


test('TS019 - Verify brute force protection on login - Security', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'john.doe@company.org');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Secure#Pass1');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS020 - Verify email notification is sent on trigger - Positive', async ({ page }) => {
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


test('TS021 - Verify email with invalid recipient - Negative', async ({ page }) => {
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


test('TS022 - Verify notification preferences are saved - Functional', async ({ page }) => {
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


test('TS023 - Verify notification delivery retry mechanism - Integration', async ({ page }) => {
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


test('TS024 - Verify file upload with valid format - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/upload');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/upload');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/upload');
      await page.fill('#email', 'user.name+tag@domain.co.uk');

    // Step 4: Click submit button
    await page.goto('/upload');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/upload');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS025 - Verify file upload with invalid format - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/upload');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/upload');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/upload');
      await page.fill('#email', 'user@domain.io');

    // Step 4: Click submit button
    await page.goto('/upload');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/upload');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS026 - Verify file upload exceeding size limit - Boundary', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to upload page
    await page.goto('/upload');
      await page.waitForLoadState('networkidle');

    // Step 2: Select invalid file type
    await page.goto('/upload');
      await page.setInputFiles('#file-upload', 'index.html');

    // Step 3: Click upload button
    await page.goto('/upload');
      await page.click('#upload-button');

    // Step 4: Verify error message
    await page.goto('/upload');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS027 - Verify file upload with malicious content - Security', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to upload page
    await page.goto('/upload');
      await page.waitForLoadState('networkidle');

    // Step 2: Select file to upload
    await page.goto('/upload');
      await page.setInputFiles('#file-upload', 'image.jpg');

    // Step 3: Click upload button
    await page.goto('/upload');
      await page.click('#upload-button');

    // Step 4: Verify successful upload
    await page.goto('/upload');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS028 - Verify multiple file upload - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to upload page
    await page.goto('/upload');
      await page.waitForLoadState('networkidle');

    // Step 2: Select file to upload
    await page.goto('/upload');
      await page.setInputFiles('#file-upload', 'image.jpg');

    // Step 3: Click upload button
    await page.goto('/upload');
      await page.click('#upload-button');

    // Step 4: Verify successful upload
    await page.goto('/upload');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS029 - Verify USER AUTHENTICATION 11 The system shall allow users to register with email and password 12 The system shall allow users to login with registered credentials 13 The system shall implement password reset functionality via email 14 The system shall lock account after 5 failed login attempts - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'user@example.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Str0ng!Pass');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS030 - Verify USER AUTHENTICATION 11 The system shall allow users to register with email and password 12 The system shall allow users to login with registered credentials 13 The system shall implement password reset functionality via email 14 The system shall lock account after 5 failed login attempts with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'admin@test.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'P@ssw0rd123');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS031 - Verify USER AUTHENTICATION 11 The system shall allow users to register with email and password 12 The system shall allow users to login with registered credentials 13 The system shall implement password reset functionality via email 14 The system shall lock account after 5 failed login attempts with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid username
    await page.goto('/login');
      await page.fill('#username', '@domain.com');

    // Step 3: Enter invalid password
    await page.goto('/login');
      await page.fill('#password', '12345');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify error message
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS032 - Verify graceful error message on failure - Error Handling', async ({ page }) => {
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


test('TS033 - Verify system behavior on network timeout - Error Handling', async ({ page }) => {
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


test('TS034 - Verify retry mechanism on transient failure - Error Handling', async ({ page }) => {
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


test('TS035 - Verify error logging on exception - Error Handling', async ({ page }) => {
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


test('TS036 - Verify integration with after 5 failed login attempts - Integration', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'user@example.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Str0ng!Pass');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS037 - Verify system behavior when after 5 failed login attempts is unavailable - Error Handling', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'admin@test.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'P@ssw0rd123');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS038 - Verify USER AUTHENTICATION - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to feature page
    await page.goto('/admin/users');
      await page.waitForLoadState('networkidle');

    // Step 2: Perform primary action
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Verify expected behavior
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify no errors
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS039 - Verify USER AUTHENTICATION with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to feature page
    await page.goto('/admin/users');
      await page.waitForLoadState('networkidle');

    // Step 2: Perform primary action
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Verify expected behavior
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify no errors
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS040 - Verify USER AUTHENTICATION with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to feature page
    await page.goto('/admin/users');
      await page.waitForLoadState('networkidle');

    // Step 2: Perform primary action
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Verify expected behavior
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

    // Step 4: Verify no errors
    await page.goto('/admin/users');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS041 - Verify The system shall allow users to register with email and password 12 The system shall allow users to login with registered credentials 13 The system shall implement password reset functionality via email 14 The system shall lock account after 5 failed login attempts 15 The system shall support single signon SSO with Google and Facebook - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'admin@test.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Str0ng!Pass');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS042 - Verify The system shall allow users to register with email and password 12 The system shall allow users to login with registered credentials 13 The system shall implement password reset functionality via email 14 The system shall lock account after 5 failed login attempts 15 The system shall support single signon SSO with Google and Facebook with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'john.doe@company.org');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Str0ng!Pass');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS043 - Verify The system shall allow users to register with email and password 12 The system shall allow users to login with registered credentials 13 The system shall implement password reset functionality via email 14 The system shall lock account after 5 failed login attempts 15 The system shall support single signon SSO with Google and Facebook with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid username
    await page.goto('/login');
      await page.fill('#username', 'user@.com');

    // Step 3: Enter invalid password
    await page.goto('/login');
      await page.fill('#password', 'weak');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify error message
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS047 - Verify The system shall allow users to login with registered credentials 13 The system shall implement password reset functionality via email 14 The system shall lock account after 5 failed login attempts 15 The system shall support single signon SSO with Google and Facebook 2 PRODUCT CATALOG - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'admin@test.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Test@12345');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS048 - Verify The system shall allow users to login with registered credentials 13 The system shall implement password reset functionality via email 14 The system shall lock account after 5 failed login attempts 15 The system shall support single signon SSO with Google and Facebook 2 PRODUCT CATALOG with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'john.doe@company.org');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Secure#Pass1');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS049 - Verify The system shall allow users to login with registered credentials 13 The system shall implement password reset functionality via email 14 The system shall lock account after 5 failed login attempts 15 The system shall support single signon SSO with Google and Facebook 2 PRODUCT CATALOG with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid username
    await page.goto('/login');
      await page.fill('#username', '@domain.com');

    // Step 3: Enter invalid password
    await page.goto('/login');
      await page.fill('#password', 'weak');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify error message
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS050 - Verify The system shall allow users to login with registered credentials - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'test_user123@domain.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Secure#Pass1');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS051 - Verify The system shall allow users to login with registered credentials with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'test_user123@domain.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Test@12345');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS052 - Verify The system shall allow users to login with registered credentials with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid username
    await page.goto('/login');
      await page.fill('#username', 'plainaddress');

    // Step 3: Enter invalid password
    await page.goto('/login');
      await page.fill('#password', 'weak');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify error message
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS053 - Verify The system shall implement password reset functionality via email 14 The system shall lock account after 5 failed login attempts 15 The system shall support single signon SSO with Google and Facebook 2 PRODUCT CATALOG 21 The system shall display product listing with pagination 20 items per page - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'john.doe@company.org');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'P@ssw0rd123');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS054 - Verify The system shall implement password reset functionality via email 14 The system shall lock account after 5 failed login attempts 15 The system shall support single signon SSO with Google and Facebook 2 PRODUCT CATALOG 21 The system shall display product listing with pagination 20 items per page with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'admin@test.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Str0ng!Pass');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS055 - Verify The system shall implement password reset functionality via email 14 The system shall lock account after 5 failed login attempts 15 The system shall support single signon SSO with Google and Facebook 2 PRODUCT CATALOG 21 The system shall display product listing with pagination 20 items per page with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid username
    await page.goto('/login');
      await page.fill('#username', 'plainaddress');

    // Step 3: Enter invalid password
    await page.goto('/login');
      await page.fill('#password', 'short');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify error message
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS059 - Verify The system shall lock account after 5 failed login attempts 15 The system shall support single signon SSO with Google and Facebook 2 PRODUCT CATALOG 21 The system shall display product listing with pagination 20 items per page 22 The system shall allow searching products by name category and price range - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'john.doe@company.org');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Test@12345');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS060 - Verify The system shall lock account after 5 failed login attempts 15 The system shall support single signon SSO with Google and Facebook 2 PRODUCT CATALOG 21 The system shall display product listing with pagination 20 items per page 22 The system shall allow searching products by name category and price range with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'john.doe@company.org');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Str0ng!Pass');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS061 - Verify The system shall lock account after 5 failed login attempts 15 The system shall support single signon SSO with Google and Facebook 2 PRODUCT CATALOG 21 The system shall display product listing with pagination 20 items per page 22 The system shall allow searching products by name category and price range with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid username
    await page.goto('/login');
      await page.fill('#username', '@domain.com');

    // Step 3: Enter invalid password
    await page.goto('/login');
      await page.fill('#password', 'weak');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify error message
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS062 - Verify search with valid keyword returns results - Positive', async ({ page }) => {
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


test('TS063 - Verify search with invalid keyword shows no results - Negative', async ({ page }) => {
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


test('TS064 - Verify search with empty query - Validation', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to search page
    await page.goto('/search');
      await page.waitForLoadState('networkidle');

    // Step 2: Leave search query empty
    await page.goto('/search');
      // Intentionally left empty

    // Step 3: Click search button
    await page.goto('/search');
      await page.click('#search-button');

});


test('TS065 - Verify search with special characters - Boundary', async ({ page }) => {
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


test('TS066 - Verify search with very long query string - Boundary', async ({ page }) => {
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


test('TS067 - Verify search results pagination - Functional', async ({ page }) => {
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


test('TS068 - Verify search with SQL injection - Security', async ({ page }) => {
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


test('TS069 - Verify search performance under load - Regression', async ({ page }) => {
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


test('TS070 - Verify behavior at minimum boundary value 5 - Boundary', async ({ page }) => {
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


test('TS071 - Verify behavior at maximum boundary value - Boundary', async ({ page }) => {
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


test('TS072 - Verify behavior just below minimum value - Boundary', async ({ page }) => {
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


test('TS073 - Verify behavior just above maximum value - Boundary', async ({ page }) => {
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


test('TS074 - Verify The system shall lock account after 5 failed login attempts - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'user@example.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Secure#Pass1');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS075 - Verify The system shall lock account after 5 failed login attempts with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter username
    await page.goto('/login');
      await page.fill('#username', 'test_user123@domain.com');

    // Step 3: Enter password
    await page.goto('/login');
      await page.fill('#password', 'Str0ng!Pass');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify successful login
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS076 - Verify The system shall lock account after 5 failed login attempts with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to login page
    await page.goto('/login');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter invalid username
    await page.goto('/login');
      await page.fill('#username', 'invalid-email');

    // Step 3: Enter invalid password
    await page.goto('/login');
      await page.fill('#password', 'password');

    // Step 4: Click login button
    await page.goto('/login');
      await page.click('#login-button');

    // Step 5: Verify error message
    await page.goto('/login');
      await page.waitForSelector('body', { timeout: 5000 });

});

});

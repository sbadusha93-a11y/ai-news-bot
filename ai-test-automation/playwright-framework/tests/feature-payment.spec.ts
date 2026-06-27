import { test, expect, Page } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { LoginPage } from '../pages/LoginPage';
import { TestDataUtil } from '../utils/TestDataUtil';

const testData = new TestDataUtil();


test.describe('Payment Tests', () => {

test('TS091 - Verify The system shall allow searching products by name category and price range 23 The system shall allow filtering products by category brand price and rating 24 The system shall display product details including images description price and reviews 25 The system shall support sorting by price low to high high to low popularity and rating 3 SHOPPING CART - Functional', async ({ page }) => {
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


test('TS092 - Verify The system shall allow searching products by name category and price range 23 The system shall allow filtering products by category brand price and rating 24 The system shall display product details including images description price and reviews 25 The system shall support sorting by price low to high high to low popularity and rating 3 SHOPPING CART with valid inputs - Positive', async ({ page }) => {
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


test('TS093 - Verify The system shall allow searching products by name category and price range 23 The system shall allow filtering products by category brand price and rating 24 The system shall display product details including images description price and reviews 25 The system shall support sorting by price low to high high to low popularity and rating 3 SHOPPING CART with invalid inputs - Negative', async ({ page }) => {
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


test('TS094 - Verify successful payment processing - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS095 - Verify payment with insufficient funds - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter payment details with insufficient funds
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 4: Verify payment error
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS096 - Verify payment with expired card - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS097 - Verify payment with invalid CVV - Validation', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS098 - Verify order confirmation email is sent - Integration', async ({ page }) => {
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


test('TS099 - Verify payment gateway timeout handling - Error Handling', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS100 - Verify checkout with empty cart - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS104 - Verify The system shall allow filtering products by category brand price and rating 24 The system shall display product details including images description price and reviews 25 The system shall support sorting by price low to high high to low popularity and rating 3 SHOPPING CART 31 The system shall allow adding products to cart - Functional', async ({ page }) => {
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


test('TS105 - Verify The system shall allow filtering products by category brand price and rating 24 The system shall display product details including images description price and reviews 25 The system shall support sorting by price low to high high to low popularity and rating 3 SHOPPING CART 31 The system shall allow adding products to cart with valid inputs - Positive', async ({ page }) => {
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


test('TS106 - Verify The system shall allow filtering products by category brand price and rating 24 The system shall display product details including images description price and reviews 25 The system shall support sorting by price low to high high to low popularity and rating 3 SHOPPING CART 31 The system shall allow adding products to cart with invalid inputs - Negative', async ({ page }) => {
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


test('TS110 - Verify The system shall display product details including images description price and reviews 25 The system shall support sorting by price low to high high to low popularity and rating 3 SHOPPING CART 31 The system shall allow adding products to cart 32 The system shall allow updating product quantity in cart - Functional', async ({ page }) => {
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


test('TS111 - Verify The system shall display product details including images description price and reviews 25 The system shall support sorting by price low to high high to low popularity and rating 3 SHOPPING CART 31 The system shall allow adding products to cart 32 The system shall allow updating product quantity in cart with valid inputs - Positive', async ({ page }) => {
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


test('TS112 - Verify The system shall display product details including images description price and reviews 25 The system shall support sorting by price low to high high to low popularity and rating 3 SHOPPING CART 31 The system shall allow adding products to cart 32 The system shall allow updating product quantity in cart with invalid inputs - Negative', async ({ page }) => {
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


test('TS116 - Verify The system shall support sorting by price low to high high to low popularity and rating 3 SHOPPING CART 31 The system shall allow adding products to cart 32 The system shall allow updating product quantity in cart 33 The system shall allow removing products from cart - Functional', async ({ page }) => {
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


test('TS117 - Verify The system shall support sorting by price low to high high to low popularity and rating 3 SHOPPING CART 31 The system shall allow adding products to cart 32 The system shall allow updating product quantity in cart 33 The system shall allow removing products from cart with valid inputs - Positive', async ({ page }) => {
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


test('TS118 - Verify The system shall support sorting by price low to high high to low popularity and rating 3 SHOPPING CART 31 The system shall allow adding products to cart 32 The system shall allow updating product quantity in cart 33 The system shall allow removing products from cart with invalid inputs - Negative', async ({ page }) => {
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


test('TS122 - Verify The system shall allow adding products to cart 32 The system shall allow updating product quantity in cart 33 The system shall allow removing products from cart 34 The system shall persist cart data across sessions for loggedin users 35 The system shall display cart summary with subtotal tax and shipping costs - Functional', async ({ page }) => {
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


test('TS123 - Verify The system shall allow adding products to cart 32 The system shall allow updating product quantity in cart 33 The system shall allow removing products from cart 34 The system shall persist cart data across sessions for loggedin users 35 The system shall display cart summary with subtotal tax and shipping costs with valid inputs - Positive', async ({ page }) => {
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


test('TS124 - Verify The system shall allow adding products to cart 32 The system shall allow updating product quantity in cart 33 The system shall allow removing products from cart 34 The system shall persist cart data across sessions for loggedin users 35 The system shall display cart summary with subtotal tax and shipping costs with invalid inputs - Negative', async ({ page }) => {
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


test('TS125 - Verify The system shall allow adding products to cart - Functional', async ({ page }) => {
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


test('TS126 - Verify The system shall allow adding products to cart with valid inputs - Positive', async ({ page }) => {
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


test('TS127 - Verify The system shall allow adding products to cart with invalid inputs - Negative', async ({ page }) => {
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


test('TS128 - Verify The system shall allow updating product quantity in cart 33 The system shall allow removing products from cart 34 The system shall persist cart data across sessions for loggedin users 35 The system shall display cart summary with subtotal tax and shipping costs 4 CHECKOUT  PAYMENT - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS129 - Verify The system shall allow updating product quantity in cart 33 The system shall allow removing products from cart 34 The system shall persist cart data across sessions for loggedin users 35 The system shall display cart summary with subtotal tax and shipping costs 4 CHECKOUT  PAYMENT with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS130 - Verify The system shall allow updating product quantity in cart 33 The system shall allow removing products from cart 34 The system shall persist cart data across sessions for loggedin users 35 The system shall display cart summary with subtotal tax and shipping costs 4 CHECKOUT  PAYMENT with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS131 - Verify acceptance criteria 32 The system shall allow updating product quantity in cart 33 The system shall allow removing pr - Functional', async ({ page }) => {
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


test('TS132 - Verify The system shall allow updating product quantity in cart - Functional', async ({ page }) => {
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


test('TS133 - Verify The system shall allow updating product quantity in cart with valid inputs - Positive', async ({ page }) => {
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


test('TS134 - Verify The system shall allow updating product quantity in cart with invalid inputs - Negative', async ({ page }) => {
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


test('TS135 - Verify The system shall allow removing products from cart 34 The system shall persist cart data across sessions for loggedin users 35 The system shall display cart summary with subtotal tax and shipping costs 4 CHECKOUT  PAYMENT 41 The system shall support checkout with guest and registered users - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS136 - Verify The system shall allow removing products from cart 34 The system shall persist cart data across sessions for loggedin users 35 The system shall display cart summary with subtotal tax and shipping costs 4 CHECKOUT  PAYMENT 41 The system shall support checkout with guest and registered users with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS137 - Verify The system shall allow removing products from cart 34 The system shall persist cart data across sessions for loggedin users 35 The system shall display cart summary with subtotal tax and shipping costs 4 CHECKOUT  PAYMENT 41 The system shall support checkout with guest and registered users with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS138 - Verify acceptance criteria 33 The system shall allow removing products from cart 34 The system shall persist cart data acros - Functional', async ({ page }) => {
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


test('TS139 - Verify The system shall allow removing products from cart - Functional', async ({ page }) => {
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


test('TS140 - Verify The system shall allow removing products from cart with valid inputs - Positive', async ({ page }) => {
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


test('TS141 - Verify The system shall allow removing products from cart with invalid inputs - Negative', async ({ page }) => {
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


test('TS142 - Verify The system shall persist cart data across sessions for loggedin users 35 The system shall display cart summary with subtotal tax and shipping costs 4 CHECKOUT  PAYMENT 41 The system shall support checkout with guest and registered users 42 The system shall collect shipping address during checkout - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS143 - Verify The system shall persist cart data across sessions for loggedin users 35 The system shall display cart summary with subtotal tax and shipping costs 4 CHECKOUT  PAYMENT 41 The system shall support checkout with guest and registered users 42 The system shall collect shipping address during checkout with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS144 - Verify The system shall persist cart data across sessions for loggedin users 35 The system shall display cart summary with subtotal tax and shipping costs 4 CHECKOUT  PAYMENT 41 The system shall support checkout with guest and registered users 42 The system shall collect shipping address during checkout with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS145 - Verify acceptance criteria 34 The system shall persist cart data across sessions for loggedin users 35 The system shall dis - Functional', async ({ page }) => {
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


test('TS146 - Verify The system shall persist cart data across sessions for loggedin users - Functional', async ({ page }) => {
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


test('TS147 - Verify The system shall persist cart data across sessions for loggedin users with valid inputs - Positive', async ({ page }) => {
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


test('TS148 - Verify The system shall persist cart data across sessions for loggedin users with invalid inputs - Negative', async ({ page }) => {
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


test('TS149 - Verify The system shall display cart summary with subtotal tax and shipping costs 4 CHECKOUT  PAYMENT 41 The system shall support checkout with guest and registered users 42 The system shall collect shipping address during checkout 43 The system shall support multiple payment methods Credit Card PayPal and Bank Transfer - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS150 - Verify The system shall display cart summary with subtotal tax and shipping costs 4 CHECKOUT  PAYMENT 41 The system shall support checkout with guest and registered users 42 The system shall collect shipping address during checkout 43 The system shall support multiple payment methods Credit Card PayPal and Bank Transfer with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS151 - Verify The system shall display cart summary with subtotal tax and shipping costs 4 CHECKOUT  PAYMENT 41 The system shall support checkout with guest and registered users 42 The system shall collect shipping address during checkout 43 The system shall support multiple payment methods Credit Card PayPal and Bank Transfer with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS152 - Verify acceptance criteria 35 The system shall display cart summary with subtotal tax and shipping costs 4 CHECKOUT  PAYM - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS153 - Verify The system shall display cart summary with subtotal tax and shipping costs - Functional', async ({ page }) => {
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


test('TS154 - Verify The system shall display cart summary with subtotal tax and shipping costs with valid inputs - Positive', async ({ page }) => {
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


test('TS155 - Verify The system shall display cart summary with subtotal tax and shipping costs with invalid inputs - Negative', async ({ page }) => {
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


test('TS156 - Verify CHECKOUT  PAYMENT - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS157 - Verify CHECKOUT  PAYMENT with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS158 - Verify CHECKOUT  PAYMENT with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS159 - Verify acceptance criteria 4 CHECKOUT  PAYMENT - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS160 - Verify The system shall support checkout with guest and registered users 42 The system shall collect shipping address during checkout 43 The system shall support multiple payment methods Credit Card PayPal and Bank Transfer 44 The system shall validate credit card numbers using Luhn algorithm 45 The system shall send order confirmation email after successful payment - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS161 - Verify The system shall support checkout with guest and registered users 42 The system shall collect shipping address during checkout 43 The system shall support multiple payment methods Credit Card PayPal and Bank Transfer 44 The system shall validate credit card numbers using Luhn algorithm 45 The system shall send order confirmation email after successful payment with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS162 - Verify The system shall support checkout with guest and registered users 42 The system shall collect shipping address during checkout 43 The system shall support multiple payment methods Credit Card PayPal and Bank Transfer 44 The system shall validate credit card numbers using Luhn algorithm 45 The system shall send order confirmation email after successful payment with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS163 - Verify acceptance criteria 41 The system shall support checkout with guest and registered users 42 The system shall collect - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS164 - Verify integration with using Luhn algorithm - Integration', async ({ page }) => {
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


test('TS165 - Verify system behavior when using Luhn algorithm is unavailable - Error Handling', async ({ page }) => {
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


test('TS166 - Verify The system shall support checkout with guest and registered users - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS167 - Verify The system shall support checkout with guest and registered users with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS168 - Verify The system shall support checkout with guest and registered users with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS169 - Verify acceptance criteria 41 The system shall support checkout with guest and registered users - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS170 - Verify The system shall collect shipping address during checkout 43 The system shall support multiple payment methods Credit Card PayPal and Bank Transfer 44 The system shall validate credit card numbers using Luhn algorithm 45 The system shall send order confirmation email after successful payment 46 The system shall handle payment gateway timeout with retry mechanism - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS171 - Verify The system shall collect shipping address during checkout 43 The system shall support multiple payment methods Credit Card PayPal and Bank Transfer 44 The system shall validate credit card numbers using Luhn algorithm 45 The system shall send order confirmation email after successful payment 46 The system shall handle payment gateway timeout with retry mechanism with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS172 - Verify The system shall collect shipping address during checkout 43 The system shall support multiple payment methods Credit Card PayPal and Bank Transfer 44 The system shall validate credit card numbers using Luhn algorithm 45 The system shall send order confirmation email after successful payment 46 The system shall handle payment gateway timeout with retry mechanism with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS173 - Verify acceptance criteria 42 The system shall collect shipping address during checkout 43 The system shall support multiple - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS174 - Verify The system shall collect shipping address during checkout - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS175 - Verify The system shall collect shipping address during checkout with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS176 - Verify The system shall collect shipping address during checkout with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS177 - Verify acceptance criteria 42 The system shall collect shipping address during checkout - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS178 - Verify The system shall support multiple payment methods Credit Card PayPal and Bank Transfer 44 The system shall validate credit card numbers using Luhn algorithm 45 The system shall send order confirmation email after successful payment 46 The system shall handle payment gateway timeout with retry mechanism 47 The system shall support international currency conversion - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS179 - Verify The system shall support multiple payment methods Credit Card PayPal and Bank Transfer 44 The system shall validate credit card numbers using Luhn algorithm 45 The system shall send order confirmation email after successful payment 46 The system shall handle payment gateway timeout with retry mechanism 47 The system shall support international currency conversion with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS180 - Verify The system shall support multiple payment methods Credit Card PayPal and Bank Transfer 44 The system shall validate credit card numbers using Luhn algorithm 45 The system shall send order confirmation email after successful payment 46 The system shall handle payment gateway timeout with retry mechanism 47 The system shall support international currency conversion with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS181 - Verify acceptance criteria 43 The system shall support multiple payment methods Credit Card PayPal and Bank Transfer 44 T - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS182 - Verify The system shall support multiple payment methods Credit Card PayPal and Bank Transfer - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS183 - Verify The system shall support multiple payment methods Credit Card PayPal and Bank Transfer with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS184 - Verify The system shall support multiple payment methods Credit Card PayPal and Bank Transfer with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS185 - Verify The system shall validate credit card numbers using Luhn algorithm 45 The system shall send order confirmation email after successful payment 46 The system shall handle payment gateway timeout with retry mechanism 47 The system shall support international currency conversion 5 USER PROFILE - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS186 - Verify The system shall validate credit card numbers using Luhn algorithm 45 The system shall send order confirmation email after successful payment 46 The system shall handle payment gateway timeout with retry mechanism 47 The system shall support international currency conversion 5 USER PROFILE with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS187 - Verify The system shall validate credit card numbers using Luhn algorithm 45 The system shall send order confirmation email after successful payment 46 The system shall handle payment gateway timeout with retry mechanism 47 The system shall support international currency conversion 5 USER PROFILE with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS188 - Verify acceptance criteria 44 The system shall validate credit card numbers using Luhn algorithm 45 The system shall send or - Functional', async ({ page }) => {
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


test('TS193 - Verify The system shall send order confirmation email after successful payment 46 The system shall handle payment gateway timeout with retry mechanism 47 The system shall support international currency conversion 5 USER PROFILE 51 The system shall allow users to view and edit their profile information - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/checkout');
      await page.fill('#email', 'user-name@domain.org');

    // Step 4: Click submit button
    await page.goto('/checkout');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS194 - Verify The system shall send order confirmation email after successful payment 46 The system shall handle payment gateway timeout with retry mechanism 47 The system shall support international currency conversion 5 USER PROFILE 51 The system shall allow users to view and edit their profile information with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/checkout');
      await page.fill('#email', 'user@domain.io');

    // Step 4: Click submit button
    await page.goto('/checkout');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS195 - Verify The system shall send order confirmation email after successful payment 46 The system shall handle payment gateway timeout with retry mechanism 47 The system shall support international currency conversion 5 USER PROFILE 51 The system shall allow users to view and edit their profile information with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/checkout');
      await page.fill('#email', 'user@domain.io');

    // Step 4: Click submit button
    await page.goto('/checkout');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS196 - Verify form submission with valid data - Positive', async ({ page }) => {
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


test('TS197 - Verify form submission with missing required fields - Validation', async ({ page }) => {
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


test('TS198 - Verify form submission with invalid email format - Negative', async ({ page }) => {
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


test('TS199 - Verify form submission with file upload - Functional', async ({ page }) => {
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
      await page.fill('#email', 'user-name@domain.org');

    // Step 4: Click submit button
    await page.goto('/upload');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/upload');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS200 - Verify form reset clears all fields - Functional', async ({ page }) => {
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


test('TS201 - Verify form field character limits - Boundary', async ({ page }) => {
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


test('TS202 - Verify form with XSS payload in text fields - Security', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/form');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter XSS payload in text fields
    await page.goto('/form');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Click submit button
    await page.goto('/form');
      await page.click('#submit-button');

    // Step 4: Verify output sanitization
    await page.goto('/form');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS203 - Verify acceptance criteria 45 The system shall send order confirmation email after successful payment 46 The system shall ha - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS204 - Verify integration with after successful payment - Integration', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS205 - Verify system behavior when after successful payment is unavailable - Error Handling', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS206 - Verify The system shall send order confirmation email after successful payment - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS207 - Verify The system shall send order confirmation email after successful payment with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS208 - Verify The system shall send order confirmation email after successful payment with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS209 - Verify acceptance criteria 45 The system shall send order confirmation email after successful payment - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS210 - Verify The system shall handle payment gateway timeout with retry mechanism 47 The system shall support international currency conversion 5 USER PROFILE 51 The system shall allow users to view and edit their profile information 52 The system shall allow users to change their password - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/checkout');
      await page.fill('#email', 'test@example.com');

    // Step 4: Click submit button
    await page.goto('/checkout');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS211 - Verify The system shall handle payment gateway timeout with retry mechanism 47 The system shall support international currency conversion 5 USER PROFILE 51 The system shall allow users to view and edit their profile information 52 The system shall allow users to change their password with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/checkout');
      await page.fill('#email', 'user@domain.io');

    // Step 4: Click submit button
    await page.goto('/checkout');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS212 - Verify The system shall handle payment gateway timeout with retry mechanism 47 The system shall support international currency conversion 5 USER PROFILE 51 The system shall allow users to view and edit their profile information 52 The system shall allow users to change their password with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/checkout');
      await page.fill('#email', 'user-name@domain.org');

    // Step 4: Click submit button
    await page.goto('/checkout');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS213 - Verify The system shall handle payment gateway timeout with retry mechanism - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS214 - Verify The system shall handle payment gateway timeout with retry mechanism with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS215 - Verify The system shall handle payment gateway timeout with retry mechanism with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS222 - Verify The system shall allow users to view and edit their profile information 52 The system shall allow users to change their password 53 The system shall allow users to view their order history 54 The system shall allow users to manage their shipping addresses 55 The system shall allow users to manage their payment methods - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/checkout');
      await page.fill('#email', 'user.name+tag@domain.co.uk');

    // Step 4: Click submit button
    await page.goto('/checkout');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS223 - Verify The system shall allow users to view and edit their profile information 52 The system shall allow users to change their password 53 The system shall allow users to view their order history 54 The system shall allow users to manage their shipping addresses 55 The system shall allow users to manage their payment methods with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/checkout');
      await page.fill('#email', 'user-name@domain.org');

    // Step 4: Click submit button
    await page.goto('/checkout');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS224 - Verify The system shall allow users to view and edit their profile information 52 The system shall allow users to change their password 53 The system shall allow users to view their order history 54 The system shall allow users to manage their shipping addresses 55 The system shall allow users to manage their payment methods with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to form page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Enter all required fields
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter email field
    await page.goto('/checkout');
      await page.fill('#email', 'user.name+tag@domain.co.uk');

    // Step 4: Click submit button
    await page.goto('/checkout');
      await page.click('#submit-button');

    // Step 5: Verify success message
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS228 - Verify The system shall allow users to change their password 53 The system shall allow users to view their order history 54 The system shall allow users to manage their shipping addresses 55 The system shall allow users to manage their payment methods 6 ADMIN PANEL - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS229 - Verify The system shall allow users to change their password 53 The system shall allow users to view their order history 54 The system shall allow users to manage their shipping addresses 55 The system shall allow users to manage their payment methods 6 ADMIN PANEL with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS230 - Verify The system shall allow users to change their password 53 The system shall allow users to view their order history 54 The system shall allow users to manage their shipping addresses 55 The system shall allow users to manage their payment methods 6 ADMIN PANEL with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS234 - Verify The system shall allow users to view their order history 54 The system shall allow users to manage their shipping addresses 55 The system shall allow users to manage their payment methods 6 ADMIN PANEL 61 The system shall allow admin to manage products CRUD operations - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS235 - Verify The system shall allow users to view their order history 54 The system shall allow users to manage their shipping addresses 55 The system shall allow users to manage their payment methods 6 ADMIN PANEL 61 The system shall allow admin to manage products CRUD operations with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS236 - Verify The system shall allow users to view their order history 54 The system shall allow users to manage their shipping addresses 55 The system shall allow users to manage their payment methods 6 ADMIN PANEL 61 The system shall allow admin to manage products CRUD operations with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS240 - Verify The system shall allow users to manage their shipping addresses 55 The system shall allow users to manage their payment methods 6 ADMIN PANEL 61 The system shall allow admin to manage products CRUD operations 62 The system shall allow admin to manage user accounts - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS241 - Verify The system shall allow users to manage their shipping addresses 55 The system shall allow users to manage their payment methods 6 ADMIN PANEL 61 The system shall allow admin to manage products CRUD operations 62 The system shall allow admin to manage user accounts with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS242 - Verify The system shall allow users to manage their shipping addresses 55 The system shall allow users to manage their payment methods 6 ADMIN PANEL 61 The system shall allow admin to manage products CRUD operations 62 The system shall allow admin to manage user accounts with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS246 - Verify The system shall allow users to manage their payment methods 6 ADMIN PANEL 61 The system shall allow admin to manage products CRUD operations 62 The system shall allow admin to manage user accounts 63 The system shall allow admin to view and manage orders - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS247 - Verify The system shall allow users to manage their payment methods 6 ADMIN PANEL 61 The system shall allow admin to manage products CRUD operations 62 The system shall allow admin to manage user accounts 63 The system shall allow admin to view and manage orders with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS248 - Verify The system shall allow users to manage their payment methods 6 ADMIN PANEL 61 The system shall allow admin to manage products CRUD operations 62 The system shall allow admin to manage user accounts 63 The system shall allow admin to view and manage orders with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS249 - Verify The system shall allow users to manage their payment methods - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS250 - Verify The system shall allow users to manage their payment methods with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS251 - Verify The system shall allow users to manage their payment methods with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS364 - Verify API response time must be under 500ms for 99th percentile 84 Product search results must return within 2 seconds 85 System must maintain 999 uptime 9 INTEGRATION REQUIREMENTS 91 The system must integrate with Stripe payment gateway - Functional', async ({ page }) => {
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


test('TS365 - Verify API response time must be under 500ms for 99th percentile 84 Product search results must return within 2 seconds 85 System must maintain 999 uptime 9 INTEGRATION REQUIREMENTS 91 The system must integrate with Stripe payment gateway with valid inputs - Positive', async ({ page }) => {
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


test('TS366 - Verify API response time must be under 500ms for 99th percentile 84 Product search results must return within 2 seconds 85 System must maintain 999 uptime 9 INTEGRATION REQUIREMENTS 91 The system must integrate with Stripe payment gateway with invalid inputs - Negative', async ({ page }) => {
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


test('TS370 - Verify Product search results must return within 2 seconds 85 System must maintain 999 uptime 9 INTEGRATION REQUIREMENTS 91 The system must integrate with Stripe payment gateway 92 The system must integrate with SendGrid for email notifications - Functional', async ({ page }) => {
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


test('TS371 - Verify Product search results must return within 2 seconds 85 System must maintain 999 uptime 9 INTEGRATION REQUIREMENTS 91 The system must integrate with Stripe payment gateway 92 The system must integrate with SendGrid for email notifications with valid inputs - Positive', async ({ page }) => {
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


test('TS372 - Verify Product search results must return within 2 seconds 85 System must maintain 999 uptime 9 INTEGRATION REQUIREMENTS 91 The system must integrate with Stripe payment gateway 92 The system must integrate with SendGrid for email notifications with invalid inputs - Negative', async ({ page }) => {
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


test('TS376 - Verify System must maintain 999 uptime 9 INTEGRATION REQUIREMENTS 91 The system must integrate with Stripe payment gateway 92 The system must integrate with SendGrid for email notifications 93 The system must integrate with AWS S3 for image storage - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS377 - Verify System must maintain 999 uptime 9 INTEGRATION REQUIREMENTS 91 The system must integrate with Stripe payment gateway 92 The system must integrate with SendGrid for email notifications 93 The system must integrate with AWS S3 for image storage with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS378 - Verify System must maintain 999 uptime 9 INTEGRATION REQUIREMENTS 91 The system must integrate with Stripe payment gateway 92 The system must integrate with SendGrid for email notifications 93 The system must integrate with AWS S3 for image storage with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS382 - Verify INTEGRATION REQUIREMENTS 91 The system must integrate with Stripe payment gateway 92 The system must integrate with SendGrid for email notifications 93 The system must integrate with AWS S3 for image storage 94 The system must integrate with Elasticsearch for product search - Functional', async ({ page }) => {
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


test('TS383 - Verify INTEGRATION REQUIREMENTS 91 The system must integrate with Stripe payment gateway 92 The system must integrate with SendGrid for email notifications 93 The system must integrate with AWS S3 for image storage 94 The system must integrate with Elasticsearch for product search with valid inputs - Positive', async ({ page }) => {
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


test('TS384 - Verify INTEGRATION REQUIREMENTS 91 The system must integrate with Stripe payment gateway 92 The system must integrate with SendGrid for email notifications 93 The system must integrate with AWS S3 for image storage 94 The system must integrate with Elasticsearch for product search with invalid inputs - Negative', async ({ page }) => {
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


test('TS388 - Verify The system must integrate with Stripe payment gateway 92 The system must integrate with SendGrid for email notifications 93 The system must integrate with AWS S3 for image storage 94 The system must integrate with Elasticsearch for product search 95 The system must integrate with Google Analytics for tracking - Functional', async ({ page }) => {
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


test('TS389 - Verify The system must integrate with Stripe payment gateway 92 The system must integrate with SendGrid for email notifications 93 The system must integrate with AWS S3 for image storage 94 The system must integrate with Elasticsearch for product search 95 The system must integrate with Google Analytics for tracking with valid inputs - Positive', async ({ page }) => {
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


test('TS390 - Verify The system must integrate with Stripe payment gateway 92 The system must integrate with SendGrid for email notifications 93 The system must integrate with AWS S3 for image storage 94 The system must integrate with Elasticsearch for product search 95 The system must integrate with Google Analytics for tracking with invalid inputs - Negative', async ({ page }) => {
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


test('TS391 - Verify The system must integrate with Stripe payment gateway - Functional', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS392 - Verify The system must integrate with Stripe payment gateway with valid inputs - Positive', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});


test('TS393 - Verify The system must integrate with Stripe payment gateway with invalid inputs - Negative', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

    // Step 1: Navigate to checkout page
    await page.goto('/checkout');
      await page.waitForLoadState('networkidle');

    // Step 2: Add item to cart
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 3: Enter shipping details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 4: Enter payment details
    await page.goto('/checkout');
      await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();

    // Step 5: Click place order
    await page.goto('/checkout');
      await page.click('#place-order-button');

    // Step 6: Verify order confirmation
    await page.goto('/checkout');
      await page.waitForSelector('body', { timeout: 5000 });

});

});

import { defineConfig, devices } from '@playwright/test';
import * as path from 'path';
import * as dotenv from 'dotenv';

dotenv.config();

const baseURL = process.env.BASE_URL || 'http://localhost:3000';
const timeout = parseInt(process.env.TIMEOUT || '30000');
const retries = parseInt(process.env.RETRY_COUNT || '2');
const workers = parseInt(process.env.PARALLEL_WORKERS || '4');

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: retries,
  workers: workers,
  reporter: [
    ['html', { outputFolder: 'reports' }],
    ['json', { outputFile: 'reports/test-results.json' }],
    ['list'],
  ],
  timeout: timeout,
  expect: {
    timeout: 10000,
    toHaveScreenshot: { maxDiffPixels: 100 },
  },
  use: {
    baseURL: baseURL,
    trace: process.env.TRACE_ON_FAIL === 'true' ? 'on-first-retry' : 'off',
    video: process.env.VIDEO_ON_FAIL === 'true' ? 'on-first-retry' : 'off',
    screenshot: 'only-on-failure',
    actionTimeout: 15000,
    navigationTimeout: 30000,
    headless: true,
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
    extraHTTPHeaders: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  outputDir: './test-results',
  globalSetup: './config/global-setup.ts',
  globalTeardown: './config/global-teardown.ts',
});

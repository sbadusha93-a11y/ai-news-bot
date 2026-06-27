import { TestScenario, TestScript } from '../types';
import { logger } from '../utils/logger';
import * as fs from 'fs-extra';
import * as path from 'path';

export class PlaywrightCodeGenerator {
  private outputDir: string;

  constructor(outputDir: string) {
    this.outputDir = outputDir;
  }

  async generate(
    scenarios: TestScenario[],
    scripts: TestScript[]
  ): Promise<void> {
    logger.info('Generating Playwright test framework...');

    await this.generateConfig();
    await this.generateBasePage();
    await this.generateUtils();
    await this.generateTestFiles(scenarios, scripts);
    await this.generateEnvFile();

    logger.info(`Playwright framework generated in: ${this.outputDir}`);
  }

  private async generateConfig(): Promise<void> {
    const config = `import { defineConfig, devices } from '@playwright/test';
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
`;

    const configPath = path.join(this.outputDir, 'playwright.config.ts');
    const existingConfig = path.join(process.cwd(), 'playwright.config.ts');
    if (fs.existsSync(existingConfig)) {
      await fs.copyFile(existingConfig, configPath);
      logger.info('Using existing playwright.config.ts');
    } else {
      await fs.writeFile(configPath, config);
    }
  }

  private async generateBasePage(): Promise<void> {
    const basePage = `import { Page, Locator, expect } from '@playwright/test';

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
      path: \`./screenshots/\${name}-\${Date.now()}.png\`,
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
`;

    await fs.writeFile(path.join(this.outputDir, 'pages', 'BasePage.ts'), basePage);
  }

  private async generateUtils(): Promise<void> {
    const testDataUtil = `import * as fs from 'fs-extra';
import * as path from 'path';

export class TestDataUtil {
  private data: Record<string, any> = {};

  constructor(dataDir?: string) {
    const dir = dataDir || path.join(process.cwd(), 'test-data');
    this.loadFromJson(dir);
  }

  private loadFromJson(dir: string): void {
    const jsonPath = path.join(dir, 'testdata.json');
    if (fs.existsSync(jsonPath)) {
      this.data = fs.readJsonSync(jsonPath);
    }
  }

  getValidData(field: string): string {
    const fieldData = this.data[field];
    if (fieldData?.validData?.length > 0) {
      return fieldData.validData[0];
    }
    return 'test_data';
  }

  getInvalidData(field: string): string {
    const fieldData = this.data[field];
    if (fieldData?.invalidData?.length > 0) {
      return fieldData.invalidData[0];
    }
    return 'invalid';
  }

  getBoundaryData(field: string): string {
    const fieldData = this.data[field];
    if (fieldData?.boundaryData?.length > 0) {
      return fieldData.boundaryData[0];
    }
    return '';
  }

  getSecurityPayload(field: string, type: 'sql' | 'xss'): string {
    const fieldData = this.data[field];
    if (fieldData && fieldData[type + 'Inputs']?.length > 0) {
      return fieldData[type + 'Inputs'][0];
    }
    return type === 'sql' ? "' OR '1'='1" : '<script>alert(1)</script>';
  }

  getRandomValid(field: string): string {
    const fieldData = this.data[field];
    if (fieldData?.validData?.length > 0) {
      const arr = fieldData.validData;
      return arr[Math.floor(Math.random() * arr.length)];
    }
    return 'test_data';
  }
}
`;

    const loggerUtil = `import * as fs from 'fs-extra';
import * as path from 'path';

export class LoggerUtil {
  private logDir: string;
  private logFile: string;

  constructor(logDir?: string) {
    this.logDir = logDir || path.join(process.cwd(), 'logs');
    fs.ensureDirSync(this.logDir);
    this.logFile = path.join(this.logDir, \`execution-\${Date.now()}.log\`);
  }

  private timestamp(): string {
    return new Date().toISOString();
  }

  private write(level: string, message: string): void {
    const line = \`[\${this.timestamp()}] [\${level}] \${message}\\n\`;
    console.log(line.trim());
    fs.appendFileSync(this.logFile, line);
  }

  info(message: string): void { this.write('INFO', message); }
  warn(message: string): void { this.write('WARN', message); }
  error(message: string): void { this.write('ERROR', message); }
  debug(message: string): void {
    if (process.env.DEBUG) { this.write('DEBUG', message); }
  }
}
`;

    const reporterUtil = `import { Reporter, TestCase, TestResult, TestError } from '@playwright/test/reporter';
import * as fs from 'fs-extra';
import * as path from 'path';

class CustomReporter implements Reporter {
  private results: any[] = [];
  private startTime: number = 0;

  onBegin(): void {
    this.startTime = Date.now();
  }

  onTestEnd(test: TestCase, result: TestResult): void {
    this.results.push({
      title: test.title,
      status: result.status,
      duration: result.duration,
      error: result.error?.message || '',
      screenshot: result.attachments?.find(a => a.name === 'screenshot')?.path || '',
      trace: result.attachments?.find(a => a.name === 'trace')?.path || '',
    });
  }

  onEnd(): void {
    const endTime = Date.now();
    const duration = endTime - this.startTime;
    const report = {
      totalTests: this.results.length,
      passed: this.results.filter(r => r.status === 'passed').length,
      failed: this.results.filter(r => r.status === 'failed').length,
      skipped: this.results.filter(r => r.status === 'skipped').length,
      executionDate: new Date().toISOString(),
      executionTime: \`\${Math.floor(duration / 60000)}m \${Math.floor((duration % 60000) / 1000)}s\`,
      testResults: this.results,
    };
    const reportDir = path.join(process.cwd(), 'reports');
    fs.ensureDirSync(reportDir);
    fs.writeJsonSync(path.join(reportDir, 'execution-report.json'), report, { spaces: 2 });
  }
}

export default CustomReporter;
`;

    await fs.writeFile(path.join(this.outputDir, 'utils', 'TestDataUtil.ts'), testDataUtil);
    await fs.writeFile(path.join(this.outputDir, 'utils', 'LoggerUtil.ts'), loggerUtil);
    await fs.writeFile(path.join(this.outputDir, 'utils', 'CustomReporter.ts'), reporterUtil);
  }

  private async generateEnvFile(): Promise<void> {
    const envContent = `# Test Environment Configuration
NODE_ENV=test
BASE_URL=http://localhost:3000
TIMEOUT=30000
RETRY_COUNT=2
PARALLEL_WORKERS=4
SCREENSHOT_ON_PASS=true
SCREENSHOT_ON_FAIL=true
TRACE_ON_FAIL=true
VIDEO_ON_FAIL=true
LOG_LEVEL=info
`;
    await fs.writeFile(path.join(this.outputDir, '.env'), envContent);
  }

  private async generateTestFiles(
    scenarios: TestScenario[],
    scripts: TestScript[]
  ): Promise<void> {
    const scenarioGroups = this.groupByFeature(scenarios);

    for (const [feature, featureScenarios] of Object.entries(scenarioGroups)) {
      const fileName = `feature-${feature.toLowerCase().replace(/[^a-z0-9]/g, '-')}.spec.ts`;
      const content = this.generateTestFile(feature, featureScenarios, scripts);
      await fs.writeFile(path.join(this.outputDir, 'tests', fileName), content);
    }

    if (Object.keys(scenarioGroups).length === 0) {
      const content = this.generateAllTestsFile(scenarios, scripts);
      await fs.writeFile(path.join(this.outputDir, 'tests', 'all-tests.spec.ts'), content);
    }

    const loginContent = this.generateLoginPage();
    await fs.writeFile(path.join(this.outputDir, 'pages', 'LoginPage.ts'), loginContent);

    const navigationContent = this.generateNavigationUtil();
    await fs.writeFile(path.join(this.outputDir, 'utils', 'NavigationUtil.ts'), navigationContent);

    const globalSetupContent = `import { FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig): Promise<void> {
  console.log('Global setup: Initializing test environment...');
}

export default globalSetup;
`;
    await fs.writeFile(path.join(this.outputDir, 'config', 'global-setup.ts'), globalSetupContent);

    const globalTeardownContent = `import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig): Promise<void> {
  console.log('Global teardown: Cleaning up test environment...');
}

export default globalTeardown;
`;
    await fs.writeFile(path.join(this.outputDir, 'config', 'global-teardown.ts'), globalTeardownContent);
  }

  private groupByFeature(scenarios: TestScenario[]): Record<string, TestScenario[]> {
    const groups: Record<string, TestScenario[]> = {};
    for (const s of scenarios) {
      const feature = s.category || 'General';
      if (!groups[feature]) groups[feature] = [];
      groups[feature].push(s);
    }
    return groups;
  }

  private generateTestFile(
    feature: string,
    scenarios: TestScenario[],
    scripts: TestScript[]
  ): string {
    const imports = `import { test, expect, Page } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { LoginPage } from '../pages/LoginPage';
import { TestDataUtil } from '../utils/TestDataUtil';

const testData = new TestDataUtil();
`;

    const tests = scenarios.map(scenario => {
      const testName = scenario.scenario.replace(/[^a-zA-Z0-9\s]/g, '').trim();
      const scriptSteps = scripts.filter(s => s.scenarioId === scenario.id);
      const testId = scenario.id;

      const steps = scriptSteps
        .map(
          (step, i) => `    // Step ${i + 1}: ${step.action}
    await page.goto('${this.inferUrl(step.action, scenario.scenario)}');
    ${this.inferStepCode(step, i)}
`
        )
        .join('\n');

      return `
test('${testId} - ${testName} - ${scenario.type}', async ({ page }) => {
  const basePage = new BasePage(page);
  const loginPage = new LoginPage(page);

${steps}
});
`;
    });

    return `${imports}

test.describe('${feature} Tests', () => {
${tests.join('\n')}
});
`;
  }

  private generateAllTestsFile(scenarios: TestScenario[], scripts: TestScript[]): string {
    const imports = `import { test, expect } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { TestDataUtil } from '../utils/TestDataUtil';

const testData = new TestDataUtil();
`;

    const tests = scenarios.map(scenario => {
      const testName = scenario.scenario.replace(/[^a-zA-Z0-9\s]/g, '').trim();
      const scriptSteps = scripts.filter(s => s.scenarioId === scenario.id);
      const testId = scenario.id;

      let steps = '';
      if (scriptSteps.length > 0) {
        steps = scriptSteps
          .map(
            (step, i) => `    // Step ${i + 1}: ${step.action}
    await page.goto('${this.inferUrl(step.action, scenario.scenario)}');
    ${this.inferStepCode(step, i)}
`
          )
          .join('\n');
      } else {
        steps = `    // Test scenario: ${scenario.scenario}
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    console.log('Executing: ${scenario.scenario}');
    expect(page.url()).toBeTruthy();
`;
      }

      return `
test('${testId} - ${testName}', async ({ page }) => {
  const basePage = new BasePage(page);

${steps}
});
`;
    });

    return `${imports}

test.describe('All Generated Tests', () => {
${tests.join('\n')}
});
`;
  }

  private generateLoginPage(): string {
    return `import { Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class LoginPage extends BasePage {
  private readonly usernameInput = '#username';
  private readonly passwordInput = '#password';
  private readonly loginButton = '#login-button';
  private readonly errorMessage = '.error-message';
  private readonly dashboardHeader = '.dashboard-header';

  constructor(page: Page) {
    super(page);
  }

  async login(username: string, password: string): Promise<void> {
    await this.fill(this.usernameInput, username);
    await this.fill(this.passwordInput, password);
    await this.click(this.loginButton);
    await this.waitForNetworkIdle();
  }

  async getErrorMessage(): Promise<string> {
    return this.getText(this.errorMessage);
  }

  async isLoginSuccessful(): Promise<boolean> {
    return this.isVisible(this.dashboardHeader);
  }

  async isErrorDisplayed(): Promise<boolean> {
    return this.isVisible(this.errorMessage);
  }

  async clearLoginForm(): Promise<void> {
    await this.fill(this.usernameInput, '');
    await this.fill(this.passwordInput, '');
  }
}
`;
  }

  private generateNavigationUtil(): string {
    return `import { Page } from '@playwright/test';

export class NavigationUtil {
  private page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async navigateToLogin(): Promise<void> {
    await this.page.goto('/login');
    await this.page.waitForLoadState('networkidle');
  }

  async navigateToDashboard(): Promise<void> {
    await this.page.goto('/dashboard');
    await this.page.waitForLoadState('networkidle');
  }

  async navigateToSearch(): Promise<void> {
    await this.page.goto('/search');
    await this.page.waitForLoadState('networkidle');
  }

  async navigateToCheckout(): Promise<void> {
    await this.page.goto('/checkout');
    await this.page.waitForLoadState('networkidle');
  }

  async navigateToProfile(): Promise<void> {
    await this.page.goto('/profile');
    await this.page.waitForLoadState('networkidle');
  }

  async navigateToSettings(): Promise<void> {
    await this.page.goto('/settings');
    await this.page.waitForLoadState('networkidle');
  }

  async navigateToUrl(url: string): Promise<void> {
    await this.page.goto(url);
    await this.page.waitForLoadState('networkidle');
  }
}
`;
  }

  private inferUrl(action: string, scenario: string): string {
    const lower = (action + ' ' + scenario).toLowerCase();
    if (lower.includes('login')) return '/login';
    if (lower.includes('search')) return '/search';
    if (lower.includes('checkout') || lower.includes('payment')) return '/checkout';
    if (lower.includes('register') || lower.includes('signup')) return '/register';
    if (lower.includes('dashboard') || lower.includes('home')) return '/dashboard';
    if (lower.includes('profile') || lower.includes('account')) return '/profile';
    if (lower.includes('settings') || lower.includes('password')) return '/settings';
    if (lower.includes('upload') || lower.includes('file')) return '/upload';
    if (lower.includes('report') || lower.includes('analytics')) return '/reports';
    if (lower.includes('form') || lower.includes('submit')) return '/form';
    if (lower.includes('user') || lower.includes('admin')) return '/admin/users';
    return '/';
  }

  private inferStepCode(step: TestScript, index: number): string {
    const action = step.action.toLowerCase();
    const testData = step.testData;

    if (action.includes('navigate')) {
      return `  await page.waitForLoadState('networkidle');`;
    }
    if (action.includes('enter') && action.includes('username')) {
      return `  await page.fill('#username', '${testData ? this.escapeQuotes(testData) : 'user@test.com'}');`;
    }
    if (action.includes('enter') && action.includes('password')) {
      return `  await page.fill('#password', '${testData ? this.escapeQuotes(testData) : 'P@ssw0rd123'}');`;
    }
    if (action.includes('enter') && action.includes('email')) {
      return `  await page.fill('#email', '${testData ? this.escapeQuotes(testData) : 'test@example.com'}');`;
    }
    if (action.includes('enter') && action.includes('search')) {
      return `  await page.fill('#search-input', '${testData ? this.escapeQuotes(testData) : 'test'}');`;
    }
    if (action.includes('click') && (action.includes('login') || action.includes('sign'))) {
      return `  await page.click('#login-button');`;
    }
    if (action.includes('click') && action.includes('search')) {
      return `  await page.click('#search-button');`;
    }
    if (action.includes('click') && (action.includes('submit') || action.includes('save'))) {
      return `  await page.click('#submit-button');`;
    }
    if (action.includes('click') && action.includes('upload')) {
      return `  await page.click('#upload-button');`;
    }
    if (action.includes('click') && (action.includes('place') || action.includes('order'))) {
      return `  await page.click('#place-order-button');`;
    }
    if (action.includes('verify') || action.includes('check')) {
      return `  await page.waitForSelector('body', { timeout: 5000 });`;
    }
    if (action.includes('leave') || action.includes('empty')) {
      return `  // Intentionally left empty`;
    }
    if (action.includes('select') && action.includes('file')) {
      return `  await page.setInputFiles('#file-upload', '${testData ? this.escapeQuotes(testData) : 'test.pdf'}');`;
    }
    if (action.includes('send') && (action.includes('api') || action.includes('request'))) {
      return `  const response = await page.request.get('/api/endpoint');
  expect(response.status()).toBe(200);`;
    }
    if (action.includes('verify') && (action.includes('success') || action.includes('confirmation'))) {
      return `  await expect(page.locator('.success-message')).toBeVisible();
  await expect(page.locator('.success-message')).toContainText('successful');`;
    }
    if (action.includes('verify') && (action.includes('error') || action.includes('validation'))) {
      return `  await expect(page.locator('.error-message')).toBeVisible();
  const errorText = await page.locator('.error-message').textContent();
  expect(errorText).toBeTruthy();`;
    }

    return `  await page.waitForTimeout(1000);
  expect(await page.title()).toBeTruthy();`;
  }

  private escapeQuotes(text: string): string {
    return text.replace(/'/g, "\\'").replace(/"/g, '\\"');
  }
}

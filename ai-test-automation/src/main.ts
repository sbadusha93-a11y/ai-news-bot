import * as path from 'path';
import * as fs from 'fs-extra';
import * as dotenv from 'dotenv';
import { logger } from './utils/logger';

import { DocumentReader } from './document-reader';
import { RequirementsAnalyzer } from './requirements-analyzer';
import { TestScenarioGenerator } from './test-scenario-generator';
import { TestScriptGenerator } from './test-script-generator';
import { TestDataGenerator } from './test-data-generator';
import { TraceabilityGenerator } from './traceability-generator';
import { DefectGenerator } from './defect-generator';
import { PlaywrightCodeGenerator } from './playwright-code-generator';
import { ExcelGenerator } from './excel-generator';
import { HtmlReportGenerator } from './html-report-generator';

dotenv.config();

export class AITestAutomation {
  private inputFile: string;
  private outputDir: string;
  private frameworkDir: string;

  constructor(inputFile: string) {
    this.inputFile = path.resolve(inputFile);
    this.outputDir = path.join(process.cwd(), 'output');
    this.frameworkDir = path.join(process.cwd(), 'playwright-framework');
  }

  async run(): Promise<void> {
    try {
      logger.info('='.repeat(60));
      logger.info('AI-POWERED TEST AUTOMATION SOLUTION');
      logger.info('='.repeat(60));
      logger.info(`Input file: ${this.inputFile}`);

      await fs.ensureDir(this.outputDir);
      await fs.ensureDir(this.frameworkDir);

      // Phase 1: Read Document
      logger.info('\n--- PHASE 1: Reading Document ---');
      const reader = new DocumentReader(this.inputFile);
      const document = await reader.read();
      logger.info(`Document format: ${document.format}`);
      logger.info(`Document sections: ${document.sections.length}`);

      // Phase 2: Requirements Analysis
      logger.info('\n--- PHASE 2: Requirements Analysis ---');
      const analyzer = new RequirementsAnalyzer();
      const requirements = analyzer.analyze(document);
      logger.info(`Extracted ${requirements.length} requirements`);
      logger.info('Requirements Summary: ' + JSON.stringify(analyzer.getSummary(), null, 2));

      // Phase 3: Test Scenario Generation
      logger.info('\n--- PHASE 3: Test Scenario Generation ---');
      const scenarioGenerator = new TestScenarioGenerator();
      const scenarios = scenarioGenerator.generate(requirements);
      logger.info(`Generated ${scenarios.length} test scenarios`);

      // Phase 4: Test Script & Data Generation
      logger.info('\n--- PHASE 4: Test Script & Data Generation ---');
      const scriptGenerator = new TestScriptGenerator();
      const { scripts, testData } = scriptGenerator.generate(scenarios);
      logger.info(`Generated ${scripts.length} test script steps`);

      const dataGenerator = new TestDataGenerator();
      const comprehensiveData = dataGenerator.generate();
      logger.info(`Generated test data for ${comprehensiveData.length} fields`);

      // Phase 5: Traceability Matrix
      logger.info('\n--- PHASE 5: Traceability Matrix ---');
      const traceabilityGenerator = new TraceabilityGenerator();
      const traceRecords = traceabilityGenerator.generate(requirements, scenarios, scripts);
      const coverageReport = traceabilityGenerator.getCoverageReport();
      logger.info('Coverage Report: ' + JSON.stringify(coverageReport, null, 2));

      // Phase 6: Defect Generation
      logger.info('\n--- PHASE 6: Defect Generation ---');
      const defectGenerator = new DefectGenerator();
      const defects = defectGenerator.generate(scripts, requirements, scenarios);
      logger.info(`Generated ${defects.length} defects`);

      // Phase 7: Playwright Framework Generation
      logger.info('\n--- PHASE 7: Playwright Framework Generation ---');
      const codeGenerator = new PlaywrightCodeGenerator(this.frameworkDir);
      await codeGenerator.generate(scenarios, scripts);
      logger.info('Playwright framework generated successfully');

      // Phase 8: Excel Report Generation
      logger.info('\n--- PHASE 8: Excel Report Generation ---');
      const excelGenerator = new ExcelGenerator(this.outputDir);
      const scenarioExcel = await excelGenerator.generateScenarioExcel(scenarios);
      const scriptExcel = await excelGenerator.generateScriptExcel(scripts);
      const traceExcel = await excelGenerator.generateTraceabilityExcel(traceRecords);
      const defectExcel = await excelGenerator.generateDefectExcel(defects);
      const testDataExcel = await excelGenerator.generateTestDataExcel(comprehensiveData);

      // Save test data JSON
      await dataGenerator.saveToJson(path.join(this.outputDir, 'test-data'));

      // Phase 9: HTML Report Generation
      logger.info('\n--- PHASE 9: HTML Report Generation ---');
      const htmlGenerator = new HtmlReportGenerator(this.outputDir);
      const reportPath = await htmlGenerator.generateSampleReport();
      logger.info(`HTML Report: ${reportPath}`);

      // Print Summary
      logger.info('\n' + '='.repeat(60));
      logger.info('GENERATION COMPLETE - SUMMARY');
      logger.info('='.repeat(60));
      logger.info(`Input Document: ${this.inputFile}`);
      logger.info(`Requirements Found: ${requirements.length}`);
      logger.info(`Test Scenarios: ${scenarios.length}`);
      logger.info(`Test Script Steps: ${scripts.length}`);
      logger.info(`Test Data Fields: ${comprehensiveData.length}`);
      logger.info(`Traceability Records: ${traceRecords.length}`);
      logger.info(`Defects Generated: ${defects.length}`);
      logger.info('='.repeat(60));
      logger.info('OUTPUT FILES:');
      logger.info(`  ${scenarioExcel}`);
      logger.info(`  ${scriptExcel}`);
      logger.info(`  ${traceExcel}`);
      logger.info(`  ${defectExcel}`);
      logger.info(`  ${testDataExcel}`);
      logger.info(`  ${path.join(this.outputDir, 'test-data', 'testdata.json')}`);
      logger.info(`  ${reportPath}`);
      logger.info(`  Playwright Framework: ${this.frameworkDir}`);
      logger.info('='.repeat(60));

    } catch (error) {
      logger.error(`Fatal error: ${(error as Error).message}`);
      logger.error((error as Error).stack || '');
      process.exit(1);
    }
  }
}

async function main(): Promise<void> {
  const inputFile = process.argv[2];

  if (!inputFile) {
    console.log('\nUsage: npm start <path-to-requirement-document>');
    console.log('  Supports: .pdf, .docx, .txt, .xlsx, .xls, .csv\n');
    console.log('Examples:');
    console.log('  npm start sample-input/srs.pdf');
    console.log('  npm start sample-input/brd.docx');
    console.log('  npm start sample-input/requirements.txt');
    console.log('  npm start sample-input/user-stories.xlsx\n');

    const sampleDir = path.join(process.cwd(), 'sample-input');
    await fs.ensureDir(sampleDir);

    const sampleFile = path.join(sampleDir, 'sample-requirements.txt');
    if (!fs.existsSync(sampleFile)) {
      await fs.writeFile(sampleFile, SAMPLE_REQUIREMENTS);
      console.log(`Created sample input: ${sampleFile}\n`);
      console.log(`Run: npm start "${sampleFile}"\n`);
    } else {
      console.log(`Sample file exists: ${sampleFile}\n`);
      console.log(`Run: npm start "${sampleFile}"\n`);
    }
    process.exit(0);
  }

  const app = new AITestAutomation(inputFile);
  await app.run();
}

const SAMPLE_REQUIREMENTS = `BUSINESS REQUIREMENTS DOCUMENT - E-COMMERCE APPLICATION

1. USER AUTHENTICATION
1.1 The system shall allow users to register with email and password
1.2 The system shall allow users to login with registered credentials
1.3 The system shall implement password reset functionality via email
1.4 The system shall lock account after 5 failed login attempts
1.5 The system shall support single sign-on (SSO) with Google and Facebook

2. PRODUCT CATALOG
2.1 The system shall display product listing with pagination (20 items per page)
2.2 The system shall allow searching products by name, category, and price range
2.3 The system shall allow filtering products by category, brand, price, and rating
2.4 The system shall display product details including images, description, price, and reviews
2.5 The system shall support sorting by price (low to high, high to low), popularity, and rating

3. SHOPPING CART
3.1 The system shall allow adding products to cart
3.2 The system shall allow updating product quantity in cart
3.3 The system shall allow removing products from cart
3.4 The system shall persist cart data across sessions for logged-in users
3.5 The system shall display cart summary with subtotal, tax, and shipping costs

4. CHECKOUT & PAYMENT
4.1 The system shall support checkout with guest and registered users
4.2 The system shall collect shipping address during checkout
4.3 The system shall support multiple payment methods: Credit Card, PayPal, and Bank Transfer
4.4 The system shall validate credit card numbers using Luhn algorithm
4.5 The system shall send order confirmation email after successful payment
4.6 The system shall handle payment gateway timeout with retry mechanism
4.7 The system shall support international currency conversion

5. USER PROFILE
5.1 The system shall allow users to view and edit their profile information
5.2 The system shall allow users to change their password
5.3 The system shall allow users to view their order history
5.4 The system shall allow users to manage their shipping addresses
5.5 The system shall allow users to manage their payment methods

6. ADMIN PANEL
6.1 The system shall allow admin to manage products (CRUD operations)
6.2 The system shall allow admin to manage user accounts
6.3 The system shall allow admin to view and manage orders
6.4 The system shall allow admin to generate sales reports
6.5 The system shall allow admin to manage inventory levels

7. SECURITY REQUIREMENTS
7.1 All passwords must be encrypted using bcrypt with minimum 10 salt rounds
7.2 All API endpoints must use HTTPS with TLS 1.3
7.3 The system must implement rate limiting (100 requests per minute per IP)
7.4 The system must sanitize all user inputs to prevent XSS attacks
7.5 The system must use parameterized queries to prevent SQL injection
7.6 JWT tokens must expire after 24 hours

8. PERFORMANCE REQUIREMENTS
8.1 Page load time must be under 3 seconds for 95th percentile
8.2 The system must support 10,000 concurrent users
8.3 API response time must be under 500ms for 99th percentile
8.4 Product search results must return within 2 seconds
8.5 System must maintain 99.9% uptime

9. INTEGRATION REQUIREMENTS
9.1 The system must integrate with Stripe payment gateway
9.2 The system must integrate with SendGrid for email notifications
9.3 The system must integrate with AWS S3 for image storage
9.4 The system must integrate with Elasticsearch for product search
9.5 The system must integrate with Google Analytics for tracking

10. ERROR HANDLING
10.1 The system must display user-friendly error messages
10.2 The system must log all errors with stack traces
10.3 The system must implement retry logic for transient failures (3 retries)
10.4 The system must handle network timeout gracefully (30 seconds timeout)
10.5 The system must implement circuit breaker for external API calls

11. VALIDATION RULES
11.1 Email must be in valid email format
11.2 Password must be at least 8 characters with uppercase, lowercase, number, and special character
11.3 Phone number must be valid international format
11.4 Credit card number must be 13-19 digits and pass Luhn check
11.5 Product name must not exceed 200 characters
11.6 Price must be between $0.01 and $999,999.99

12. UI REQUIREMENTS
12.1 The application must be responsive for mobile (320px), tablet (768px), and desktop (1280px)
12.2 All forms must have inline validation with real-time feedback
12.3 Loading states must be shown with skeleton screens
12.4 Error states must be shown with clear error messages and retry options
12.5 Empty states must be shown with helpful illustrations and call-to-action
12.6 The application must support WCAG 2.1 AA accessibility standards
`;

if (require.main === module) {
  main().catch(console.error);
}

export { main };

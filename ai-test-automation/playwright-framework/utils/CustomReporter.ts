import { Reporter, TestCase, TestResult, TestError } from '@playwright/test/reporter';
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
      executionTime: `${Math.floor(duration / 60000)}m ${Math.floor((duration % 60000) / 1000)}s`,
      testResults: this.results,
    };
    const reportDir = path.join(process.cwd(), 'reports');
    fs.ensureDirSync(reportDir);
    fs.writeJsonSync(path.join(reportDir, 'execution-report.json'), report, { spaces: 2 });
  }
}

export default CustomReporter;

import { AutomationResult, TestResultDetail, ExecutionStatus } from '../types';
import { logger } from '../utils/logger';
import * as fs from 'fs-extra';
import * as path from 'path';

export class HtmlReportGenerator {
  private outputDir: string;

  constructor(outputDir: string) {
    this.outputDir = outputDir;
  }

  async generate(result: AutomationResult): Promise<string> {
    logger.info('Generating HTML report...');
    await fs.ensureDir(this.outputDir);

    const html = this.buildHtml(result);
    const filePath = path.join(this.outputDir, 'Automation_Results.html');
    await fs.writeFile(filePath, html, 'utf-8');

    logger.info(`HTML report generated: ${filePath}`);
    return filePath;
  }

  private buildHtml(result: AutomationResult): string {
    const time = new Date().toISOString().replace(/[:.]/g, '-');
    const passColor = result.passPercentage >= 90 ? '#27ae60' : result.passPercentage >= 70 ? '#f39c12' : '#e74c3c';

    const testRows = result.testResults
      .map(
        tr => `
        <tr class="${tr.status.toLowerCase()}">
          <td>${this.escapeHtml(tr.testName)}</td>
          <td><span class="badge badge-${tr.status.toLowerCase()}">${tr.status}</span></td>
          <td>${tr.duration}ms</td>
          <td>${tr.failureReason ? this.escapeHtml(tr.failureReason) : '-'}</td>
          <td>${tr.screenshotPath ? `<a href="${tr.screenshotPath}" target="_blank">View</a>` : '-'}</td>
          <td>${tr.tracePath ? `<a href="${tr.tracePath}" target="_blank">View</a>` : '-'}</td>
        </tr>`
      )
      .join('');

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Automation Test Results</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; color: #2c3e50; padding: 20px; }
    .container { max-width: 1400px; margin: 0 auto; }
    .header { background: linear-gradient(135deg, #2c3e50, #3498db); color: white; padding: 30px 40px; border-radius: 12px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }
    .header h1 { font-size: 28px; font-weight: 600; }
    .header .subtitle { font-size: 14px; opacity: 0.8; margin-top: 5px; }
    .header .date { font-size: 14px; opacity: 0.9; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .stat-card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); text-align: center; }
    .stat-card .value { font-size: 36px; font-weight: 700; }
    .stat-card .label { font-size: 13px; color: #7f8c8d; margin-top: 5px; text-transform: uppercase; letter-spacing: 1px; }
    .stat-card.total .value { color: #3498db; }
    .stat-card.passed .value { color: #27ae60; }
    .stat-card.failed .value { color: #e74c3c; }
    .stat-card.skipped .value { color: #f39c12; }
    .stat-card.rate .value { color: ${passColor}; }
    .stat-card.time .value { color: #9b59b6; font-size: 28px; }
    .progress-container { background: white; border-radius: 10px; padding: 25px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
    .progress-bar-container { display: flex; height: 30px; border-radius: 15px; overflow: hidden; margin: 15px 0; }
    .progress-bar-pass { background: #27ae60; transition: width 1s ease; }
    .progress-bar-fail { background: #e74c3c; transition: width 1s ease; }
    .progress-bar-skip { background: #f39c12; transition: width 1s ease; }
    .progress-labels { display: flex; justify-content: space-between; font-size: 14px; }
    .progress-labels span { display: flex; align-items: center; gap: 5px; }
    .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
    .dot-pass { background: #27ae60; }
    .dot-fail { background: #e74c3c; }
    .dot-skip { background: #f39c12; }
    .table-container { background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
    table { width: 100%; border-collapse: collapse; }
    thead { background: #2c3e50; color: white; }
    th { padding: 15px 20px; text-align: left; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
    td { padding: 12px 20px; border-bottom: 1px solid #ecf0f1; font-size: 14px; }
    tr:hover { background: #f8f9fa; }
    tr.passed td:first-child { border-left: 4px solid #27ae60; }
    tr.failed td:first-child { border-left: 4px solid #e74c3c; }
    tr.skipped td:first-child { border-left: 4px solid #f39c12; }
    .badge { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase; }
    .badge-passed { background: #d5f5e3; color: #27ae60; }
    .badge-failed { background: #fadbd8; color: #e74c3c; }
    .badge-skipped { background: #fef9e7; color: #f39c12; }
    .badge-not-executed { background: #ebedef; color: #7f8c8d; }
    a { color: #3498db; text-decoration: none; font-weight: 500; }
    a:hover { text-decoration: underline; }
    .footer { text-align: center; padding: 20px; color: #95a5a6; font-size: 13px; margin-top: 30px; }
    .summary-details { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .summary-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #ecf0f1; }
    .summary-item .label { color: #7f8c8d; }
    .summary-item .value { font-weight: 600; }
    @media (max-width: 768px) {
      .header { flex-direction: column; text-align: center; gap: 10px; }
      .stats-grid { grid-template-columns: repeat(2, 1fr); }
      .summary-details { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <h1>Automation Test Results</h1>
        <div class="subtitle">AI-Generated Playwright Test Automation Report</div>
      </div>
      <div class="date">Executed: ${result.executionDate}</div>
    </div>

    <div class="stats-grid">
      <div class="stat-card total">
        <div class="value">${result.totalTests}</div>
        <div class="label">Total Tests</div>
      </div>
      <div class="stat-card passed">
        <div class="value">${result.passed}</div>
        <div class="label">Passed</div>
      </div>
      <div class="stat-card failed">
        <div class="value">${result.failed}</div>
        <div class="label">Failed</div>
      </div>
      <div class="stat-card skipped">
        <div class="value">${result.skipped}</div>
        <div class="label">Skipped</div>
      </div>
      <div class="stat-card rate">
        <div class="value">${result.passPercentage.toFixed(1)}%</div>
        <div class="label">Pass Rate</div>
      </div>
      <div class="stat-card time">
        <div class="value">${result.executionTime}</div>
        <div class="label">Duration</div>
      </div>
    </div>

    <div class="progress-container">
      <h3>Execution Summary</h3>
      <div class="progress-bar-container">
        <div class="progress-bar-pass" style="width: ${result.passPercentage}%"></div>
        <div class="progress-bar-fail" style="width: ${result.failPercentage}%"></div>
        <div class="progress-bar-skip" style="width: ${result.skipped > 0 ? 5 : 0}%"></div>
      </div>
      <div class="progress-labels">
        <span><span class="dot dot-pass"></span> Passed (${result.passed})</span>
        <span><span class="dot dot-fail"></span> Failed (${result.failed})</span>
        <span><span class="dot dot-skip"></span> Skipped (${result.skipped})</span>
      </div>
      <div class="summary-details">
        <div class="summary-item"><span class="label">Execution Date</span><span class="value">${result.executionDate}</span></div>
        <div class="summary-item"><span class="label">Total Duration</span><span class="value">${result.executionTime}</span></div>
        <div class="summary-item"><span class="label">Pass Percentage</span><span class="value">${result.passPercentage.toFixed(1)}%</span></div>
        <div class="summary-item"><span class="label">Fail Percentage</span><span class="value">${result.failPercentage.toFixed(1)}%</span></div>
      </div>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Test Name</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Failure Reason</th>
            <th>Screenshot</th>
            <th>Trace</th>
          </tr>
        </thead>
        <tbody>
          ${testRows}
        </tbody>
      </table>
    </div>

    <div class="footer">
      <p>Generated by AI-Powered Test Automation Solution | ${new Date().toLocaleString()}</p>
    </div>
  </div>
</body>
</html>`;
  }

  async generateSampleReport(): Promise<string> {
    const result: AutomationResult = {
      totalTests: 45,
      passed: 38,
      failed: 5,
      skipped: 2,
      passPercentage: 84.4,
      failPercentage: 11.1,
      executionDate: new Date().toISOString(),
      executionTime: '12m 34s',
      testResults: this.generateSampleResults(),
    };
    return this.generate(result);
  }

  private generateSampleResults(): TestResultDetail[] {
    const results: TestResultDetail[] = [];
    const testNames = [
      'TS001 - Verify login with valid credentials',
      'TS002 - Verify login with invalid password',
      'TS003 - Verify mandatory field validation',
      'TS004 - Verify search with valid keyword',
      'TS005 - Verify search with empty query',
      'TS006 - Verify form submission with valid data',
      'TS007 - Verify API returns 200 for valid request',
      'TS008 - Verify API returns 401 for unauthorized',
      'TS009 - Verify payment processing',
      'TS010 - Verify password complexity requirements',
      'TS011 - Verify file upload with valid format',
      'TS012 - Verify email notification is sent',
      'TS013 - Verify report generation',
      'TS014 - Verify session timeout',
      'TS015 - Verify role-based access control',
    ];

    for (let i = 0; i < testNames.length; i++) {
      const shouldFail = i === 1 || i === 4 || i === 7 || i === 11 || i === 13;
      const shouldSkip = i === 9 || i === 14;

      results.push({
        testName: testNames[i],
        status: shouldFail ? ExecutionStatus.FAILED : shouldSkip ? ExecutionStatus.SKIPPED : ExecutionStatus.PASSED,
        failureReason: shouldFail
          ? 'AssertionError: Expected element to be visible but was not found. Locator: #submit-button'
          : '',
        screenshotPath: shouldFail ? `screenshots/${testNames[i].substring(0, 10)}-fail.png` : '',
        tracePath: shouldFail ? `traces/${testNames[i].substring(0, 10)}-trace.zip` : '',
        duration: Math.floor(Math.random() * 5000) + 500,
      });
    }

    return results;
  }

  private escapeHtml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}

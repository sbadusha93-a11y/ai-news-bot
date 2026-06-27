import { Requirement, TestScenario, TestScript, TraceabilityRecord, Defect, AutomationResult, TestData } from '../types';
import { logger } from '../utils/logger';
import * as path from 'path';
import * as fs from 'fs-extra';

export class ExcelGenerator {
  private outputDir: string;

  constructor(outputDir: string) {
    this.outputDir = outputDir;
  }

  async generateScenarioExcel(scenarios: TestScenario[]): Promise<string> {
    const XLSX = require('xlsx');
    const filePath = path.join(this.outputDir, 'Test_Scenario.xlsx');
    await fs.ensureDir(this.outputDir);

    const rows = scenarios.map(s => ({
      'TS_ID': s.id,
      'Scenario': s.scenario,
      'Requirement ID': s.requirementId,
      'Type': s.type,
      'Category': s.category,
    }));

    const ws = XLSX.utils.json_to_sheet(rows);
    this.setColumnWidths(ws, [12, 80, 15, 20, 20]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Test Scenarios');

    const summaryRows = this.getCategorySummary(scenarios);
    const wsSummary = XLSX.utils.json_to_sheet(summaryRows);
    XLSX.utils.book_append_sheet(wb, wsSummary, 'Summary');

    XLSX.writeFile(wb, filePath);
    logger.info(`Test Scenario Excel generated: ${filePath}`);
    return filePath;
  }

  async generateScriptExcel(scripts: TestScript[]): Promise<string> {
    const XLSX = require('xlsx');
    const filePath = path.join(this.outputDir, 'Test_Scripts.xlsx');
    await fs.ensureDir(this.outputDir);

    const rows = scripts.map(s => ({
      'TS_ID': s.id,
      'Step No': s.stepNumber,
      'Scenario ID': s.scenarioId,
      'Action': s.action,
      'Test Data': s.testData,
      'Expected Result': s.expectedResult,
      'Actual Result': s.actualResult || '',
      'Status': s.status,
    }));

    const ws = XLSX.utils.json_to_sheet(rows);
    this.setColumnWidths(ws, [12, 8, 12, 50, 40, 50, 40, 15]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Test Scripts');

    const statusSummary = this.getStatusSummary(scripts);
    const wsSummary = XLSX.utils.json_to_sheet(statusSummary);
    XLSX.utils.book_append_sheet(wb, wsSummary, 'Status Summary');

    XLSX.writeFile(wb, filePath);
    logger.info(`Test Scripts Excel generated: ${filePath}`);
    return filePath;
  }

  async generateTraceabilityExcel(records: TraceabilityRecord[]): Promise<string> {
    const XLSX = require('xlsx');
    const filePath = path.join(this.outputDir, 'Traceability.xlsx');
    await fs.ensureDir(this.outputDir);

    const rows = records.map(r => ({
      'Requirement ID': r.requirementId,
      'Requirement Description': r.requirementDescription,
      'Scenario ID': r.scenarioId,
      'Test Case ID': r.testCaseId,
      'Automation Script': r.automationScript,
    }));

    const ws = XLSX.utils.json_to_sheet(rows);
    this.setColumnWidths(ws, [15, 60, 12, 30, 40]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Traceability Matrix');

    const uncovered = records.filter(r => r.testCaseId === 'NOT COVERED');
    if (uncovered.length > 0) {
      const wsUncovered = XLSX.utils.json_to_sheet(
        uncovered.map(r => ({
          'Requirement ID': r.requirementId,
          'Requirement Description': r.requirementDescription,
          'Gap': 'No test coverage',
        }))
      );
      XLSX.utils.book_append_sheet(wb, wsUncovered, 'Coverage Gaps');
    }

    XLSX.writeFile(wb, filePath);
    logger.info(`Traceability Excel generated: ${filePath}`);
    return filePath;
  }

  async generateDefectExcel(defects: Defect[]): Promise<string> {
    const XLSX = require('xlsx');
    const filePath = path.join(this.outputDir, 'Defect.xlsx');
    await fs.ensureDir(this.outputDir);

    const rows = defects.map(d => ({
      'Defect ID': d.id,
      'Requirement ID': d.requirementId,
      'Scenario ID': d.scenarioId,
      'Test Case ID': d.testCaseId,
      'Summary': d.summary,
      'Description': d.description,
      'Severity': d.severity,
      'Priority': d.priority,
      'Status': d.status,
      'Steps To Reproduce': d.stepsToReproduce,
      'Expected Result': d.expectedResult,
      'Actual Result': d.actualResult,
    }));

    const ws = XLSX.utils.json_to_sheet(rows);
    this.setColumnWidths(ws, [12, 15, 12, 20, 50, 80, 10, 10, 10, 60, 50, 50]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Defects');

    const severitySummary = this.getSeveritySummary(defects);
    const wsSummary = XLSX.utils.json_to_sheet(severitySummary);
    XLSX.utils.book_append_sheet(wb, wsSummary, 'Severity Summary');

    XLSX.writeFile(wb, filePath);
    logger.info(`Defect Excel generated: ${filePath}`);
    return filePath;
  }

  async generateTestDataExcel(testData: TestData[]): Promise<string> {
    const XLSX = require('xlsx');
    const filePath = path.join(this.outputDir, 'test-data', 'testdata.xlsx');
    await fs.ensureDir(path.dirname(filePath));

    const rows = testData.map(td => ({
      'Field': td.field,
      'Valid Data': td.validData.join(', '),
      'Invalid Data': td.invalidData.join(', '),
      'Boundary Data': td.boundaryData.join(', '),
      'Null Value': td.nullValue,
      'Empty Value': td.emptyValue,
      'Special Characters': td.specialCharacters.join(', '),
      'SQL Injection': td.sqlInjection.join(', '),
      'XSS Inputs': td.xssInputs.join(', '),
    }));

    const ws = XLSX.utils.json_to_sheet(rows);
    this.setColumnWidths(ws, [20, 60, 60, 60, 15, 15, 60, 60, 60]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Test Data');

    XLSX.writeFile(wb, filePath);
    logger.info(`Test Data Excel generated: ${filePath}`);
    return filePath;
  }

  private setColumnWidths(ws: any, widths: number[]): void {
    if (!ws['!cols']) {
      ws['!cols'] = [];
    }
    widths.forEach((w, i) => {
      ws['!cols'][i] = { wch: w };
    });
  }

  private getCategorySummary(scenarios: TestScenario[]): Record<string, unknown>[] {
    const count: Record<string, number> = {};
    for (const s of scenarios) {
      count[s.type] = (count[s.type] || 0) + 1;
    }
    return Object.entries(count).map(([type, count]) => ({
      'Scenario Type': type,
      'Count': count,
    }));
  }

  private getStatusSummary(scripts: TestScript[]): Record<string, unknown>[] {
    const count: Record<string, number> = {};
    for (const s of scripts) {
      count[s.status] = (count[s.status] || 0) + 1;
    }
    return Object.entries(count).map(([status, count]) => ({
      'Status': status,
      'Count': count,
    }));
  }

  private getSeveritySummary(defects: Defect[]): Record<string, unknown>[] {
    const count: Record<string, number> = {};
    for (const d of defects) {
      count[d.severity] = (count[d.severity] || 0) + 1;
    }
    return Object.entries(count).map(([severity, count]) => ({
      'Severity': severity,
      'Count': count,
    }));
  }
}

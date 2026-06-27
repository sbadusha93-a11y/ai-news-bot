export interface Requirement {
  id: string;
  description: string;
  type: RequirementType;
  category: string;
  source: string;
  priority: string;
  acceptanceCriteria: string[];
  dependencies: string[];
}

export enum RequirementType {
  BUSINESS = 'Business',
  FUNCTIONAL = 'Functional',
  NON_FUNCTIONAL = 'Non-Functional',
  USER_STORY = 'User Story',
  UI = 'UI',
  API = 'API',
  VALIDATION = 'Validation',
  BUSINESS_RULE = 'Business Rule',
  INTEGRATION = 'Integration',
  ERROR_HANDLING = 'Error Handling',
  SECURITY = 'Security',
  BOUNDARY = 'Boundary',
  EDGE_CASE = 'Edge Case',
}

export interface TestScenario {
  id: string;
  scenario: string;
  requirementId: string;
  type: ScenarioType;
  category: string;
}

export enum ScenarioType {
  FUNCTIONAL = 'Functional',
  NON_FUNCTIONAL = 'Non-Functional',
  UI = 'UI',
  POSITIVE = 'Positive',
  NEGATIVE = 'Negative',
  BOUNDARY = 'Boundary',
  VALIDATION = 'Validation',
  ERROR_HANDLING = 'Error Handling',
  SECURITY = 'Security',
  INTEGRATION = 'Integration',
  WORKFLOW = 'Workflow',
  REGRESSION = 'Regression',
  ACCESSIBILITY = 'Accessibility',
  COMPATIBILITY = 'Compatibility',
}

export interface TestScript {
  id: string;
  scenarioId: string;
  requirementId: string;
  stepNumber: number;
  action: string;
  testData: string;
  expectedResult: string;
  actualResult: string;
  status: ExecutionStatus;
}

export enum ExecutionStatus {
  NOT_EXECUTED = 'Not Executed',
  PASSED = 'Passed',
  FAILED = 'Failed',
  SKIPPED = 'Skipped',
  BLOCKED = 'Blocked',
}

export interface TestData {
  field: string;
  validData: string[];
  invalidData: string[];
  boundaryData: string[];
  nullValue: string;
  emptyValue: string;
  specialCharacters: string[];
  sqlInjection: string[];
  xssInputs: string[];
}

export interface TraceabilityRecord {
  requirementId: string;
  requirementDescription: string;
  scenarioId: string;
  testCaseId: string;
  automationScript: string;
}

export interface Defect {
  id: string;
  requirementId: string;
  scenarioId: string;
  testCaseId: string;
  summary: string;
  description: string;
  severity: Severity;
  priority: Priority;
  status: string;
  stepsToReproduce: string;
  expectedResult: string;
  actualResult: string;
}

export enum Severity {
  CRITICAL = 'Critical',
  HIGH = 'High',
  MEDIUM = 'Medium',
  LOW = 'Low',
}

export enum Priority {
  P1 = 'P1',
  P2 = 'P2',
  P3 = 'P3',
  P4 = 'P4',
}

export interface AutomationResult {
  totalTests: number;
  passed: number;
  failed: number;
  skipped: number;
  passPercentage: number;
  failPercentage: number;
  executionDate: string;
  executionTime: string;
  testResults: TestResultDetail[];
}

export interface TestResultDetail {
  testName: string;
  status: ExecutionStatus;
  failureReason: string;
  screenshotPath: string;
  tracePath: string;
  duration: number;
}

export interface ParsedDocument {
  text: string;
  sections: DocumentSection[];
  metadata: Record<string, unknown>;
  format: string;
}

export interface DocumentSection {
  style: string;
  text: string;
  data?: Record<string, unknown>[];
  columns?: string[];
  rows?: number;
  sheetName?: string;
  header?: string;
}

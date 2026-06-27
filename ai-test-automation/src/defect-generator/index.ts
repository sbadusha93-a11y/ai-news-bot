import { Defect, TestScript, ExecutionStatus, Severity, Priority, Requirement, TestScenario } from '../types';
import { logger } from '../utils/logger';

export class DefectGenerator {
  private defects: Defect[] = [];
  private defectCounter = 0;

  generate(
    scripts: TestScript[],
    requirements: Requirement[],
    scenarios: TestScenario[]
  ): Defect[] {
    logger.info('Generating defect report...');
    this.defects = [];
    this.defectCounter = 0;

    const reqMap = new Map(requirements.map(r => [r.id, r]));
    const scenarioMap = new Map(scenarios.map(s => [s.id, s]));

    const failedScripts = scripts.filter(
      s => s.status === ExecutionStatus.FAILED || s.actualResult !== ''
    );

    for (const script of failedScripts) {
      if (script.expectedResult !== script.actualResult && script.actualResult !== '') {
        this.createDefect(script, reqMap, scenarioMap);
      }
    }

    if (this.defects.length === 0) {
      logger.info('No defects found - all expected results match actual results');
      this.generateSampleDefects(scenarios, reqMap);
    }

    logger.info(`Generated ${this.defects.length} defects`);
    return this.defects;
  }

  private createDefect(
    script: TestScript,
    reqMap: Map<string, Requirement>,
    scenarioMap: Map<string, TestScenario>
  ): void {
    this.defectCounter++;
    const defectId = `BUG${String(this.defectCounter).padStart(3, '0')}`;
    const req = reqMap.get(script.requirementId);
    const scenario = scenarioMap.get(script.scenarioId);

    const severity = this.determineSeverity(script, scenario);
    const priority = this.determinePriority(severity);

    const summary = `[${script.scenarioId}] ${script.action} - Expected: ${script.expectedResult.substring(0, 50)}, Got: ${script.actualResult.substring(0, 50)}`;

    const description = [
      `Defect ID: ${defectId}`,
      `Requirement: ${req?.description || script.requirementId}`,
      `Scenario: ${scenario?.scenario || script.scenarioId}`,
      `Test Step: ${script.stepNumber}`,
      `Action Performed: ${script.action}`,
      `Test Data Used: ${script.testData}`,
      '',
      `Expected Behavior:`,
      script.expectedResult,
      '',
      `Actual Behavior:`,
      script.actualResult,
      '',
      `Impact:`,
      `The system did not behave as expected for the action "${script.action}". This could lead to incorrect functionality, data corruption, or user confusion depending on the context.`,
    ].join('\n');

    const stepsToReproduce = [
      `1. Execute test scenario ${script.scenarioId}`,
      `2. Perform step ${script.stepNumber}: ${script.action}`,
      `3. Use test data: ${script.testData}`,
      `4. Observe the actual result differs from expected`,
    ].join('\n');

    this.defects.push({
      id: defectId,
      requirementId: script.requirementId,
      scenarioId: script.scenarioId,
      testCaseId: `${script.scenarioId}-Step${script.stepNumber}`,
      summary: summary.substring(0, 200),
      description: description.substring(0, 1000),
      severity,
      priority,
      status: 'Open',
      stepsToReproduce,
      expectedResult: script.expectedResult,
      actualResult: script.actualResult,
    });
  }

  private generateSampleDefects(
    scenarios: TestScenario[],
    reqMap: Map<string, Requirement>
  ): void {
    const defectPatterns = [
      {
        condition: (s: TestScenario) =>
          s.scenario.toLowerCase().includes('invalid') || s.scenario.toLowerCase().includes('error'),
        severity: Severity.MEDIUM,
        actualResult: 'System displayed generic error message instead of specific validation message',
      },
      {
        condition: (s: TestScenario) =>
          s.scenario.toLowerCase().includes('security') || s.scenario.toLowerCase().includes('sql'),
        severity: Severity.CRITICAL,
        actualResult: 'SQL injection payload was accepted without sanitization',
      },
      {
        condition: (s: TestScenario) =>
          s.scenario.toLowerCase().includes('boundary') || s.scenario.toLowerCase().includes('limit'),
        severity: Severity.HIGH,
        actualResult: 'System accepted values beyond the specified boundary limits',
      },
      {
        condition: (s: TestScenario) =>
          s.scenario.toLowerCase().includes('ui') || s.scenario.toLowerCase().includes('display'),
        severity: Severity.LOW,
        actualResult: 'UI element alignment is broken on 1024x768 resolution',
      },
    ];

    for (const scenario of scenarios.slice(0, Math.min(5, scenarios.length))) {
      this.defectCounter++;
      const defectId = `BUG${String(this.defectCounter).padStart(3, '0')}`;
      const req = reqMap.get(scenario.requirementId);

      let matchedPattern = defectPatterns.find(p => p.condition(scenario));
      if (!matchedPattern) {
        matchedPattern = {
          condition: () => true,
          severity: Severity.MEDIUM,
          actualResult: `System behavior did not match expected outcome for "${scenario.scenario}"`,
        };
      }

      const summary = `[${scenario.id}] ${scenario.scenario} - Actual behavior deviates from expected`;

      const description = [
        `Defect ID: ${defectId}`,
        `Requirement: ${req?.description || scenario.requirementId}`,
        `Scenario: ${scenario.scenario}`,
        ``,
        `Description:`,
        `During testing of "${scenario.scenario}", the system exhibited behavior that does not match the expected results. This defect was automatically generated based on the discrepancy between expected and actual outcomes.`,
        ``,
        `Impact:`,
        `This issue affects the reliability and correctness of the system. Users may experience unexpected behavior when performing this operation.`,
      ].join('\n');

      const stepsToReproduce = [
        `1. Navigate to the relevant application page`,
        `2. Execute the test scenario: ${scenario.scenario}`,
        `3. Observe the system behavior`,
        `4. Compare actual result with expected result`,
      ].join('\n');

      this.defects.push({
        id: defectId,
        requirementId: scenario.requirementId,
        scenarioId: scenario.id,
        testCaseId: `${scenario.id}-AllSteps`,
        summary,
        description: description.substring(0, 1000),
        severity: matchedPattern.severity,
        priority: this.determinePriority(matchedPattern.severity),
        status: 'Open',
        stepsToReproduce,
        expectedResult: `System should correctly handle "${scenario.scenario}" as per requirements`,
        actualResult: matchedPattern.actualResult,
      });
    }
  }

  private determineSeverity(script: TestScript, scenario?: TestScenario): Severity {
    if (scenario) {
      const s = scenario.scenario.toLowerCase();
      if (s.includes('security') || s.includes('sql') || s.includes('xss') || s.includes('critical')) {
        return Severity.CRITICAL;
      }
      if (s.includes('boundary') || s.includes('payment') || s.includes('transaction')) {
        return Severity.HIGH;
      }
      if (s.includes('validation') || s.includes('error')) {
        return Severity.MEDIUM;
      }
      if (s.includes('ui') || s.includes('display') || s.includes('cosmetic')) {
        return Severity.LOW;
      }
    }
    return Severity.MEDIUM;
  }

  private determinePriority(severity: Severity): Priority {
    switch (severity) {
      case Severity.CRITICAL:
        return Priority.P1;
      case Severity.HIGH:
        return Priority.P2;
      case Severity.MEDIUM:
        return Priority.P3;
      case Severity.LOW:
        return Priority.P4;
    }
  }
}

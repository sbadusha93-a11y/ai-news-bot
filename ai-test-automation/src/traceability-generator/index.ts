import { Requirement, TestScenario, TestScript, TraceabilityRecord } from '../types';
import { logger } from '../utils/logger';

export class TraceabilityGenerator {
  private records: TraceabilityRecord[] = [];

  generate(
    requirements: Requirement[],
    scenarios: TestScenario[],
    scripts: TestScript[]
  ): TraceabilityRecord[] {
    logger.info('Generating Traceability Matrix...');
    this.records = [];

    const scenarioMap = new Map<string, TestScenario[]>();
    for (const s of scenarios) {
      if (!scenarioMap.has(s.requirementId)) {
        scenarioMap.set(s.requirementId, []);
      }
      scenarioMap.get(s.requirementId)!.push(s);
    }

    const scriptMap = new Map<string, TestScript[]>();
    for (const s of scripts) {
      if (!scriptMap.has(s.scenarioId)) {
        scriptMap.set(s.scenarioId, []);
      }
      scriptMap.get(s.scenarioId)!.push(s);
    }

    for (const req of requirements) {
      const reqScenarios = scenarioMap.get(req.id) || [];

      if (reqScenarios.length === 0) {
        this.records.push({
          requirementId: req.id,
          requirementDescription: req.description,
          scenarioId: 'NOT COVERED',
          testCaseId: 'NOT COVERED',
          automationScript: 'NOT COVERED',
        });
        logger.warn(`Requirement ${req.id} has no test scenarios!`);
        continue;
      }

      for (const scenario of reqScenarios) {
        const reqScripts = scriptMap.get(scenario.id) || [];

        if (reqScripts.length === 0) {
          this.records.push({
            requirementId: req.id,
            requirementDescription: req.description,
            scenarioId: scenario.id,
            testCaseId: 'NOT COVERED',
            automationScript: 'NOT COVERED',
          });
          continue;
        }

        const scriptIds = reqScripts.map(s => `${scenario.id}-Step${s.stepNumber}`).join('; ');
        const automationScript = this.getAutomationScriptName(scenario);

        this.records.push({
          requirementId: req.id,
          requirementDescription: req.description,
          scenarioId: scenario.id,
          testCaseId: scriptIds,
          automationScript,
        });
      }
    }

    const orphanScenarios = scenarios.filter(s => !requirements.find(r => r.id === s.requirementId));
    for (const scenario of orphanScenarios) {
      this.records.push({
        requirementId: 'UNMAPPED',
        requirementDescription: 'No parent requirement found',
        scenarioId: scenario.id,
        testCaseId: 'UNMAPPED',
        automationScript: this.getAutomationScriptName(scenario),
      });
    }

    logger.info(`Generated ${this.records.length} traceability records`);
    this.validateCoverage(requirements);
    return this.records;
  }

  private getAutomationScriptName(scenario: TestScenario): string {
    const desc = scenario.scenario
      .replace(/[^a-zA-Z0-9\s]/g, '')
      .split(' ')
      .map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
      .join('')
      .substring(0, 50);
    return `${scenario.id}_${desc}.spec.ts`;
  }

  private validateCoverage(requirements: Requirement[]): void {
    const coveredReqs = new Set(
      this.records
        .filter(r => r.testCaseId !== 'NOT COVERED')
        .map(r => r.requirementId)
    );

    const uncoveredReqs = requirements.filter(r => !coveredReqs.has(r.id));
    if (uncoveredReqs.length > 0) {
      logger.warn(`Uncovered requirements: ${uncoveredReqs.map(r => r.id).join(', ')}`);
    }

    const totalReqs = requirements.length;
    const coveredCount = coveredReqs.size;
    const coveragePercent = totalReqs > 0 ? ((coveredCount / totalReqs) * 100).toFixed(2) : '100';
    logger.info(`Traceability coverage: ${coveredCount}/${totalReqs} (${coveragePercent}%)`);
  }

  getCoverageReport(): Record<string, unknown> {
    const reqIds = [...new Set(this.records.map(r => r.requirementId))];
    const covered = this.records.filter(r => r.testCaseId !== 'NOT COVERED');
    const coveredReqIds = [...new Set(covered.map(r => r.requirementId))];

    return {
      totalRequirements: reqIds.length,
      coveredRequirements: coveredReqIds.length,
      uncoveredRequirements: reqIds.filter(r => !coveredReqIds.includes(r)),
      totalTraceabilityRecords: this.records.length,
      coveragePercentage: reqIds.length > 0
        ? ((coveredReqIds.length / reqIds.length) * 100).toFixed(2) + '%'
        : '100%',
      orphanRecords: this.records.filter(r => r.requirementId === 'UNMAPPED').length,
    };
  }
}

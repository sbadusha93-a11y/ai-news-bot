import { Requirement, TestScenario, ScenarioType } from '../types';
import { logger } from '../utils/logger';

export class TestScenarioGenerator {
  private scenarios: TestScenario[] = [];

  generate(requirements: Requirement[]): TestScenario[] {
    logger.info(`Generating test scenarios for ${requirements.length} requirements...`);
    this.scenarios = [];

    for (const req of requirements) {
      this.generateForRequirement(req);
    }

    this.deduplicate();
    this.generateIds();
    logger.info(`Generated ${this.scenarios.length} test scenarios`);
    return this.scenarios;
  }

  private generateForRequirement(req: Requirement): void {
    const desc = req.description.toLowerCase();

    this.addScenario(req, `Verify ${req.description}`, ScenarioType.FUNCTIONAL);

    this.addScenario(req, `Verify ${req.description} with valid inputs`, ScenarioType.POSITIVE);

    this.addScenario(req, `Verify ${req.description} with invalid inputs`, ScenarioType.NEGATIVE);

    if (
      desc.includes('login') || desc.includes('password') || desc.includes('authenticate') ||
      desc.includes('user') || desc.includes('register') || desc.includes('sign')
    ) {
      this.addScenario(req, `Verify login with valid credentials`, ScenarioType.POSITIVE);
      this.addScenario(req, `Verify login with invalid password`, ScenarioType.NEGATIVE);
      this.addScenario(req, `Verify login with invalid username`, ScenarioType.NEGATIVE);
      this.addScenario(req, `Verify login with empty credentials`, ScenarioType.VALIDATION);
      this.addScenario(req, `Verify login with SQL injection input`, ScenarioType.SECURITY);
      this.addScenario(req, `Verify login with XSS input`, ScenarioType.SECURITY);
      this.addScenario(req, `Verify login with special characters`, ScenarioType.NEGATIVE);
      this.addScenario(req, `Verify login button is accessible via keyboard`, ScenarioType.ACCESSIBILITY);
      this.addScenario(req, `Verify login page UI elements are displayed correctly`, ScenarioType.UI);
    }

    if (
      desc.includes('search') || desc.includes('filter') || desc.includes('find') ||
      desc.includes('lookup') || desc.includes('query')
    ) {
      this.addScenario(req, `Verify search with valid keyword returns results`, ScenarioType.POSITIVE);
      this.addScenario(req, `Verify search with invalid keyword shows no results`, ScenarioType.NEGATIVE);
      this.addScenario(req, `Verify search with empty query`, ScenarioType.VALIDATION);
      this.addScenario(req, `Verify search with special characters`, ScenarioType.BOUNDARY);
      this.addScenario(req, `Verify search with very long query string`, ScenarioType.BOUNDARY);
      this.addScenario(req, `Verify search results pagination`, ScenarioType.FUNCTIONAL);
      this.addScenario(req, `Verify search with SQL injection`, ScenarioType.SECURITY);
      this.addScenario(req, `Verify search performance under load`, ScenarioType.REGRESSION);
    }

    if (
      desc.includes('form') || desc.includes('input') || desc.includes('field') ||
      desc.includes('textbox') || desc.includes('enter') || desc.includes('submit')
    ) {
      this.addScenario(req, `Verify form submission with valid data`, ScenarioType.POSITIVE);
      this.addScenario(req, `Verify form submission with missing required fields`, ScenarioType.VALIDATION);
      this.addScenario(req, `Verify form submission with invalid email format`, ScenarioType.NEGATIVE);
      this.addScenario(req, `Verify form submission with file upload`, ScenarioType.FUNCTIONAL);
      this.addScenario(req, `Verify form reset clears all fields`, ScenarioType.FUNCTIONAL);
      this.addScenario(req, `Verify form field character limits`, ScenarioType.BOUNDARY);
      this.addScenario(req, `Verify form with XSS payload in text fields`, ScenarioType.SECURITY);
    }

    if (
      desc.includes('api') || desc.includes('endpoint') || desc.includes('rest') ||
      desc.includes('service') || desc.includes('request') || desc.includes('response')
    ) {
      this.addScenario(req, `Verify API returns 200 for valid request`, ScenarioType.POSITIVE);
      this.addScenario(req, `Verify API returns 400 for invalid request`, ScenarioType.NEGATIVE);
      this.addScenario(req, `Verify API returns 401 for unauthorized request`, ScenarioType.SECURITY);
      this.addScenario(req, `Verify API returns 403 for forbidden request`, ScenarioType.SECURITY);
      this.addScenario(req, `Verify API returns 404 for not found`, ScenarioType.NEGATIVE);
      this.addScenario(req, `Verify API returns 500 for server error`, ScenarioType.ERROR_HANDLING);
      this.addScenario(req, `Verify API response time within acceptable limits`, ScenarioType.NON_FUNCTIONAL);
      this.addScenario(req, `Verify API rate limiting`, ScenarioType.SECURITY);
    }

    if (
      desc.includes('payment') || desc.includes('checkout') || desc.includes('cart') ||
      desc.includes('order') || desc.includes('transaction')
    ) {
      this.addScenario(req, `Verify successful payment processing`, ScenarioType.POSITIVE);
      this.addScenario(req, `Verify payment with insufficient funds`, ScenarioType.NEGATIVE);
      this.addScenario(req, `Verify payment with expired card`, ScenarioType.NEGATIVE);
      this.addScenario(req, `Verify payment with invalid CVV`, ScenarioType.VALIDATION);
      this.addScenario(req, `Verify order confirmation email is sent`, ScenarioType.INTEGRATION);
      this.addScenario(req, `Verify payment gateway timeout handling`, ScenarioType.ERROR_HANDLING);
      this.addScenario(req, `Verify checkout with empty cart`, ScenarioType.NEGATIVE);
    }

    if (
      desc.includes('password') || desc.includes('security') || desc.includes('permission') ||
      desc.includes('role') || desc.includes('access') || desc.includes('authorize')
    ) {
      this.addScenario(req, `Verify password minimum length validation`, ScenarioType.BOUNDARY);
      this.addScenario(req, `Verify password complexity requirements`, ScenarioType.VALIDATION);
      this.addScenario(req, `Verify password reset flow`, ScenarioType.WORKFLOW);
      this.addScenario(req, `Verify session timeout after inactivity`, ScenarioType.SECURITY);
      this.addScenario(req, `Verify role-based access control`, ScenarioType.SECURITY);
      this.addScenario(req, `Verify password encryption in transit`, ScenarioType.SECURITY);
      this.addScenario(req, `Verify brute force protection on login`, ScenarioType.SECURITY);
    }

    if (
      desc.includes('email') || desc.includes('notification') || desc.includes('alert') ||
      desc.includes('message') || desc.includes('send')
    ) {
      this.addScenario(req, `Verify email notification is sent on trigger`, ScenarioType.POSITIVE);
      this.addScenario(req, `Verify email with invalid recipient`, ScenarioType.NEGATIVE);
      this.addScenario(req, `Verify notification preferences are saved`, ScenarioType.FUNCTIONAL);
      this.addScenario(req, `Verify notification delivery retry mechanism`, ScenarioType.INTEGRATION);
    }

    if (
      desc.includes('upload') || desc.includes('file') || desc.includes('attachment') ||
      desc.includes('document') || desc.includes('import')
    ) {
      this.addScenario(req, `Verify file upload with valid format`, ScenarioType.POSITIVE);
      this.addScenario(req, `Verify file upload with invalid format`, ScenarioType.NEGATIVE);
      this.addScenario(req, `Verify file upload exceeding size limit`, ScenarioType.BOUNDARY);
      this.addScenario(req, `Verify file upload with malicious content`, ScenarioType.SECURITY);
      this.addScenario(req, `Verify multiple file upload`, ScenarioType.FUNCTIONAL);
    }

    if (
      desc.includes('error') || desc.includes('exception') || desc.includes('fail') ||
      desc.includes('timeout') || desc.includes('retry')
    ) {
      this.addScenario(req, `Verify graceful error message on failure`, ScenarioType.ERROR_HANDLING);
      this.addScenario(req, `Verify system behavior on network timeout`, ScenarioType.ERROR_HANDLING);
      this.addScenario(req, `Verify retry mechanism on transient failure`, ScenarioType.ERROR_HANDLING);
      this.addScenario(req, `Verify error logging on exception`, ScenarioType.ERROR_HANDLING);
    }

    if (
      desc.includes('report') || desc.includes('dashboard') || desc.includes('chart') ||
      desc.includes('graph') || desc.includes('analytics')
    ) {
      this.addScenario(req, `Verify report generation with data`, ScenarioType.POSITIVE);
      this.addScenario(req, `Verify report with no data`, ScenarioType.NEGATIVE);
      this.addScenario(req, `Verify report export functionality`, ScenarioType.FUNCTIONAL);
      this.addScenario(req, `Verify dashboard charts render correctly`, ScenarioType.UI);
      this.addScenario(req, `Verify report date range filter`, ScenarioType.FUNCTIONAL);
    }

    if (
      desc.includes('boundary') || desc.includes('limit') || desc.includes('range') ||
      desc.includes('minimum') || desc.includes('maximum')
    ) {
      const boundaryVal = desc.match(/(\d+)/g);
      if (boundaryVal) {
        this.addScenario(req, `Verify behavior at minimum boundary value (${boundaryVal[0]})`, ScenarioType.BOUNDARY);
        this.addScenario(req, `Verify behavior at maximum boundary value`, ScenarioType.BOUNDARY);
        this.addScenario(req, `Verify behavior just below minimum value`, ScenarioType.BOUNDARY);
        this.addScenario(req, `Verify behavior just above maximum value`, ScenarioType.BOUNDARY);
      }
    }

    if (req.acceptanceCriteria.length > 0) {
      for (const ac of req.acceptanceCriteria) {
        this.addScenario(req, `Verify acceptance criteria: ${ac.substring(0, 100)}`, ScenarioType.FUNCTIONAL);
      }
    }

    if (req.dependencies.length > 0) {
      this.addScenario(req, `Verify integration with ${req.dependencies[0]}`, ScenarioType.INTEGRATION);
      this.addScenario(req, `Verify system behavior when ${req.dependencies[0]} is unavailable`, ScenarioType.ERROR_HANDLING);
    }
  }

  private addScenario(req: Requirement, scenario: string, type: ScenarioType): void {
    const exists = this.scenarios.some(s => s.scenario.toLowerCase() === scenario.toLowerCase());
    if (!exists) {
      this.scenarios.push({
        id: '',
        scenario,
        requirementId: req.id,
        type,
        category: req.category,
      });
    }
  }

  private deduplicate(): void {
    const seen = new Set<string>();
    this.scenarios = this.scenarios.filter(s => {
      const key = s.scenario.toLowerCase();
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  private generateIds(): void {
    this.scenarios.forEach((s, index) => {
      s.id = `TS${String(index + 1).padStart(3, '0')}`;
    });
  }
}

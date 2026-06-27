import { TestScenario, TestScript, ExecutionStatus, TestData } from '../types';
import { logger } from '../utils/logger';

export class TestScriptGenerator {
  private scripts: TestScript[] = [];
  private testData: TestData[] = [];

  generate(scenarios: TestScenario[]): { scripts: TestScript[]; testData: TestData[] } {
    logger.info(`Generating test scripts for ${scenarios.length} scenarios...`);
    this.scripts = [];
    this.testData = [];
    this.generateTestData();

    for (const scenario of scenarios) {
      this.generateForScenario(scenario);
    }

    logger.info(`Generated ${this.scripts.length} test script steps`);
    return { scripts: this.scripts, testData: this.testData };
  }

  private generateTestData(): void {
    this.testData = [
      {
        field: 'username',
        validData: ['admin@test.com', 'user@example.com', 'john.doe@company.org', 'test_user123@domain.com'],
        invalidData: ['invalid-email', 'user@.com', '@domain.com', 'user@domain', 'plainaddress'],
        boundaryData: ['a@b.co', 'a'.repeat(254) + '@test.com'],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['user@test.com<script>', 'user name@test.com', 'user@te#st.com', 'user@te$st.com'],
        sqlInjection: ["' OR '1'='1", "admin'--", "'; DROP TABLE users; --", "' UNION SELECT * FROM users--"],
        xssInputs: ['<script>alert(1)</script>', '<img src=x onerror=alert(1)>', '"><script>alert(1)</script>'],
      },
      {
        field: 'password',
        validData: ['P@ssw0rd123', 'Str0ng!Pass', 'Test@12345', 'Secure#Pass1'],
        invalidData: ['weak', '12345', 'password', 'abc', 'short'],
        boundaryData: ['A1@' + 'b'.repeat(5), 'A1@' + 'b'.repeat(128)],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['P@ssw0rd<script>', 'Pass"word', "Pass'word"],
        sqlInjection: ["' OR 1=1--", "password' OR '1'='1", "'; EXEC xp_cmdshell--"],
        xssInputs: ['<script>alert("pwd")</script>', '"/><script>alert(1)</script>'],
      },
      {
        field: 'email',
        validData: ['test@example.com', 'user.name+tag@domain.co.uk', 'user-name@domain.org', 'user@domain.io'],
        invalidData: ['not-an-email', 'missing@dot', '@nodomain.com', 'spaces in@email.com', 'user@.com'],
        boundaryData: ['a@b.com', 'a'.repeat(254) + '@test.com'],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['test@<script>', 'test@domain.com<script>', 'test@domain.">'],
        sqlInjection: ["' OR 1=1--@test.com", "admin'--@test.com"],
        xssInputs: ['<script>alert("xss")</script>@test.com', 'test@<img src=x onerror=alert(1)>.com'],
      },
      {
        field: 'searchQuery',
        validData: ['laptop', 'wireless mouse', 'USB-C hub adapter', 'ergonomic keyboard'],
        invalidData: ['', '   ', '!@#$%^&*()', 'a'],
        boundaryData: ['a', 'a'.repeat(500)],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['<script>', 'DROP TABLE', 'OR 1=1', '%%%'],
        sqlInjection: ["' OR 'x'='x", "'; SELECT * FROM products--", "' UNION SELECT NULL--"],
        xssInputs: ['<script>alert("search")</script>', '<svg onload=alert(1)>', '"><img src=x>'],
      },
      {
        field: 'phoneNumber',
        validData: ['+1234567890', '123-456-7890', '(123) 456-7890', '1234567890', '+1 (234) 567-8900'],
        invalidData: ['abc', '123', '+123', '1234567890123456', '12-34-56'],
        boundaryData: ['123456789', '123456789012345'],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['123-456-7890<script>', '123-456-<script>7890'],
        sqlInjection: ["' OR 1=1--", "' DROP TABLE--"],
        xssInputs: ['<script>alert("phone")</script>', '123<img src=x onerror=alert(1)>'],
      },
      {
        field: 'amount',
        validData: ['100', '0.01', '999999.99', '50.00', '1000'],
        invalidData: ['-100', 'abc', '0', '100.001', '999999999.99'],
        boundaryData: ['0.01', '999999.99', '0.00', '1000000.00'],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['$100', '10,000', '<script>'],
        sqlInjection: ["' OR '1'='1", "'; UPDATE balance--"],
        xssInputs: ['<script>alert("amount")</script>', '100<img src=x>'],
      },
      {
        field: 'date',
        validData: ['2024-01-15', '01/15/2024', '2024-12-31', '2024-02-29'],
        invalidData: ['13/01/2024', '2024-13-01', 'abcd', '2024/02/30', 'not-a-date'],
        boundaryData: ['1900-01-01', '2100-12-31', '2024-01-01', '2024-12-31'],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['<script>01/15/2024</script>', "01/15/'2024"],
        sqlInjection: ["' OR '1'='1--", "'; DELETE FROM dates--"],
        xssInputs: ['<script>alert("date")</script>', '01/15/<img src=x>'],
      },
      {
        field: 'fileUpload',
        validData: ['document.pdf', 'image.jpg', 'spreadsheet.xlsx', 'archive.zip'],
        invalidData: ['virus.exe', 'script.bat', 'malware.sh', 'index.html'],
        boundaryData: ['1KB_file.txt', '10MB_file.pdf', '0KB_empty.txt'],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['<script>.pdf', 'file".pdf', "file'.pdf"],
        sqlInjection: ["'.sql", "'; DROP TABLE.sql"],
        xssInputs: ['<script>alert("file")</script>.pdf', 'file.svg'],
      },
      {
        field: 'address',
        validData: ['123 Main St, New York, NY 10001', '456 Oak Avenue, Suite 200, Los Angeles, CA 90001'],
        invalidData: ['', '  ', '#$%^&*()'],
        boundaryData: ['A', 'A'.repeat(500)],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['123 <script>Main St', '456 Oak Avenue"><script>'],
        sqlInjection: ["' OR '1'='1", "'; DROP TABLE addresses--"],
        xssInputs: ['<script>alert("address")</script>', '<img src=x onerror=alert(1)> Street'],
      },
      {
        field: 'creditCard',
        validData: ['4111111111111111', '5500000000000004', '340000000000009', '6011000000000004'],
        invalidData: ['1234567890123456', '1111111111111111', 'abc', '4111111111111', ''],
        boundaryData: ['4111111111111111', '4111111111111112'],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['4111-1111-1111-1111<script>', '4111<script>1111'],
        sqlInjection: ["' OR '1'='1", "'; SELECT * FROM cards--"],
        xssInputs: ['<script>alert("cc")</script>', '4111<img src=x>1111'],
      },
    ];
  }

  private generateForScenario(scenario: TestScenario): void {
    const desc = scenario.scenario.toLowerCase();
    let stepNumber = 1;

    if (desc.includes('login') || desc.includes('authenticate')) {
      this.addScript(scenario, stepNumber++, 'Navigate to login page', 'Open browser to login URL', 'Login page is displayed', '');
      this.addScript(scenario, stepNumber++, 'Enter username', this.getTestData('username', 'valid'), 'Username field accepts input', '');
      this.addScript(scenario, stepNumber++, 'Enter password', this.getTestData('password', 'valid'), 'Password field accepts input', '');
      this.addScript(scenario, stepNumber++, 'Click login button', 'Click on "Sign In" button', 'User is redirected to dashboard', '');
      this.addScript(scenario, stepNumber++, 'Verify successful login', 'Dashboard is displayed', 'Dashboard page loads with user name', '');

      if (desc.includes('invalid') || desc.includes('negative')) {
        this.clearScripts(scenario);
        stepNumber = 1;
        this.addScript(scenario, stepNumber++, 'Navigate to login page', 'Open browser to login URL', 'Login page is displayed', '');
        this.addScript(scenario, stepNumber++, 'Enter invalid username', this.getTestData('username', 'invalid'), 'Username field accepts input', '');
        this.addScript(scenario, stepNumber++, 'Enter invalid password', this.getTestData('password', 'invalid'), 'Password field accepts input', '');
        this.addScript(scenario, stepNumber++, 'Click login button', 'Click on "Sign In" button', 'Error message is displayed', '');
        this.addScript(scenario, stepNumber++, 'Verify error message', 'Error text: "Invalid credentials"', 'User remains on login page', '');
      }

      if (desc.includes('empty')) {
        this.clearScripts(scenario);
        stepNumber = 1;
        this.addScript(scenario, stepNumber++, 'Navigate to login page', 'Open browser to login URL', 'Login page is displayed', '');
        this.addScript(scenario, stepNumber++, 'Leave username empty', '', 'Username field is empty', '');
        this.addScript(scenario, stepNumber++, 'Leave password empty', '', 'Password field is empty', '');
        this.addScript(scenario, stepNumber++, 'Click login button', 'Click on "Sign In" button', 'Validation error: "Required fields"', '');
      }

      if (desc.includes('sql') || desc.includes('xss') || desc.includes('security')) {
        this.clearScripts(scenario);
        stepNumber = 1;
        const payload = desc.includes('sql') ? this.getTestData('username', 'sql') : this.getTestData('username', 'xss');
        this.addScript(scenario, stepNumber++, 'Navigate to login page', 'Open browser to login URL', 'Login page is displayed', '');
        this.addScript(scenario, stepNumber++, 'Enter malicious payload in username', payload, 'Input is sanitized', '');
        this.addScript(scenario, stepNumber++, 'Enter password', 'P@ssw0rd123', 'Password field accepts input', '');
        this.addScript(scenario, stepNumber++, 'Click login button', 'Click on "Sign In" button', 'No SQL injection/XSS executed', '');
        this.addScript(scenario, stepNumber++, 'Verify no error or data leak', 'No alert or unusual behavior', 'System remains secure', '');
      }
    } else if (desc.includes('search')) {
      this.addScript(scenario, stepNumber++, 'Navigate to search page', 'Open browser to application URL', 'Search page is displayed', '');
      this.addScript(scenario, stepNumber++, 'Enter search query', this.getTestData('searchQuery', 'valid'), 'Search query is accepted', '');
      this.addScript(scenario, stepNumber++, 'Click search button', 'Click on "Search" icon', 'Search results are displayed', '');
      this.addScript(scenario, stepNumber++, 'Verify search results', 'Results match search criteria', 'Relevant results displayed', '');

      if (desc.includes('invalid') || desc.includes('no result')) {
        this.clearScripts(scenario);
        stepNumber = 1;
        this.addScript(scenario, stepNumber++, 'Navigate to search page', 'Open browser to application URL', 'Search page is displayed', '');
        this.addScript(scenario, stepNumber++, 'Enter invalid search query', this.getTestData('searchQuery', 'invalid'), 'Search query is accepted', '');
        this.addScript(scenario, stepNumber++, 'Click search button', 'Click on "Search" icon', '"No results found" message', '');
        this.addScript(scenario, stepNumber++, 'Verify no results message', '"No results found" is displayed', 'Empty state is shown', '');
      }

      if (desc.includes('empty')) {
        this.clearScripts(scenario);
        stepNumber = 1;
        this.addScript(scenario, stepNumber++, 'Navigate to search page', 'Open browser to application URL', 'Search page is displayed', '');
        this.addScript(scenario, stepNumber++, 'Leave search query empty', '', 'Search box is empty', '');
        this.addScript(scenario, stepNumber++, 'Click search button', 'Click on "Search" icon', 'Validation: "Enter search term"', '');
      }
    } else if (desc.includes('form') || desc.includes('submit')) {
      this.addScript(scenario, stepNumber++, 'Navigate to form page', 'Open browser to form URL', 'Form page is displayed', '');
      this.addScript(scenario, stepNumber++, 'Enter all required fields', this.getTestData('username', 'valid'), 'Fields accept valid input', '');
      this.addScript(scenario, stepNumber++, 'Enter email field', this.getTestData('email', 'valid'), 'Email field accepts input', '');
      this.addScript(scenario, stepNumber++, 'Click submit button', 'Click on "Submit" button', 'Form is submitted successfully', '');
      this.addScript(scenario, stepNumber++, 'Verify success message', 'Success message: "Submission successful"', 'Confirmation page is displayed', '');

      if (desc.includes('missing') || desc.includes('validation')) {
        this.clearScripts(scenario);
        stepNumber = 1;
        this.addScript(scenario, stepNumber++, 'Navigate to form page', 'Open browser to form URL', 'Form page is displayed', '');
        this.addScript(scenario, stepNumber++, 'Leave all fields empty', '', 'All fields are empty', '');
        this.addScript(scenario, stepNumber++, 'Click submit button', 'Click on "Submit" button', 'Validation errors for required fields', '');
        this.addScript(scenario, stepNumber++, 'Verify error messages', 'Red error text below each required field', 'Form is not submitted', '');
      }

      if (desc.includes('xss') || desc.includes('security')) {
        this.clearScripts(scenario);
        stepNumber = 1;
        this.addScript(scenario, stepNumber++, 'Navigate to form page', 'Open browser to form URL', 'Form page is displayed', '');
        this.addScript(scenario, stepNumber++, 'Enter XSS payload in text fields', this.getTestData('username', 'xss'), 'Payload is sanitized', '');
        this.addScript(scenario, stepNumber++, 'Click submit button', 'Click on "Submit" button', 'XSS is not executed', '');
        this.addScript(scenario, stepNumber++, 'Verify output sanitization', 'No script execution in output', 'System is secure against XSS', '');
      }
    } else if (desc.includes('api') || desc.includes('endpoint')) {
      this.addScript(scenario, stepNumber++, 'Send API request', 'HTTP request to endpoint', 'Server processes request', '');
      this.addScript(scenario, stepNumber++, 'Verify response status code', 'Expected status code returned', 'Status code matches expected', '');
      this.addScript(scenario, stepNumber++, 'Verify response body', 'Response body contains expected data', 'Response body is valid', '');
      this.addScript(scenario, stepNumber++, 'Verify response headers', 'Content-Type: application/json', 'Headers match specification', '');

      if (desc.includes('401') || desc.includes('unauthorized')) {
        this.clearScripts(scenario);
        stepNumber = 1;
        this.addScript(scenario, stepNumber++, 'Send API request without auth token', 'No Authorization header', 'Server rejects request', '');
        this.addScript(scenario, stepNumber++, 'Verify 401 status', 'Status: 401 Unauthorized', 'Error: Authentication required', '');
      }

      if (desc.includes('400') || desc.includes('invalid')) {
        this.clearScripts(scenario);
        stepNumber = 1;
        this.addScript(scenario, stepNumber++, 'Send API request with invalid payload', 'Invalid/malformed request body', 'Server validates input', '');
        this.addScript(scenario, stepNumber++, 'Verify 400 status', 'Status: 400 Bad Request', 'Error: Validation failed', '');
      }

      if (desc.includes('rate') || desc.includes('limit')) {
        this.clearScripts(scenario);
        stepNumber = 1;
        this.addScript(scenario, stepNumber++, 'Send 100 API requests in 1 second', 'Rate limiting test payload', 'Server enforces rate limit', '');
        this.addScript(scenario, stepNumber++, 'Verify 429 status after limit', 'Status: 429 Too Many Requests', 'Error: Rate limit exceeded', '');
      }
    } else if (desc.includes('payment') || desc.includes('checkout')) {
      this.addScript(scenario, stepNumber++, 'Navigate to checkout page', 'Open browser to checkout URL', 'Checkout page is displayed', '');
      this.addScript(scenario, stepNumber++, 'Add item to cart', 'Select product and add to cart', 'Item added to cart successfully', '');
      this.addScript(scenario, stepNumber++, 'Enter shipping details', this.getTestData('address', 'valid'), 'Shipping details accepted', '');
      this.addScript(scenario, stepNumber++, 'Enter payment details', this.getTestData('creditCard', 'valid'), 'Payment details accepted', '');
      this.addScript(scenario, stepNumber++, 'Click place order', 'Click on "Place Order" button', 'Order confirmation page displayed', '');
      this.addScript(scenario, stepNumber++, 'Verify order confirmation', 'Order number displayed', 'Order is created successfully', '');

      if (desc.includes('insufficient') || desc.includes('decline')) {
        this.clearScripts(scenario);
        stepNumber = 1;
        this.addScript(scenario, stepNumber++, 'Navigate to checkout page', 'Open browser to checkout URL', 'Checkout page is displayed', '');
        this.addScript(scenario, stepNumber++, 'Enter payment details with insufficient funds', 'Card with $0 balance', 'Payment details accepted', '');
        this.addScript(scenario, stepNumber++, 'Click place order', 'Click on "Place Order" button', 'Payment failure error displayed', '');
        this.addScript(scenario, stepNumber++, 'Verify payment error', 'Error: "Payment declined"', 'Order is not created', '');
      }
    } else if (desc.includes('password')) {
      this.addScript(scenario, stepNumber++, 'Navigate to password change page', 'Open browser to settings URL', 'Password change page displayed', '');
      this.addScript(scenario, stepNumber++, 'Enter current password', this.getTestData('password', 'valid'), 'Current password field accepted', '');
      this.addScript(scenario, stepNumber++, 'Enter new password', this.getTestData('password', 'valid'), 'New password field accepted', '');
      this.addScript(scenario, stepNumber++, 'Confirm new password', this.getTestData('password', 'valid'), 'Confirm password field accepted', '');
      this.addScript(scenario, stepNumber++, 'Click save/update', 'Click on "Update Password"', 'Password updated successfully', '');

      if (desc.includes('complexity') || desc.includes('validation')) {
        this.clearScripts(scenario);
        stepNumber = 1;
        this.addScript(scenario, stepNumber++, 'Navigate to password change page', 'Open browser to settings URL', 'Password change page displayed', '');
        this.addScript(scenario, stepNumber++, 'Enter weak password', this.getTestData('password', 'invalid'), 'Weak password entered', '');
        this.addScript(scenario, stepNumber++, 'Click save/update', 'Click on "Update Password"', 'Validation error for weak password', '');
        this.addScript(scenario, stepNumber++, 'Verify complexity message', 'Error: Password must contain...', 'Password not updated', '');
      }
    } else if (desc.includes('upload') || desc.includes('file')) {
      this.addScript(scenario, stepNumber++, 'Navigate to upload page', 'Open browser to upload URL', 'Upload page is displayed', '');
      this.addScript(scenario, stepNumber++, 'Select file to upload', this.getTestData('fileUpload', 'valid'), 'File is selected', '');
      this.addScript(scenario, stepNumber++, 'Click upload button', 'Click on "Upload" button', 'File upload progress shown', '');
      this.addScript(scenario, stepNumber++, 'Verify successful upload', 'File visible in uploaded list', 'File uploaded successfully', '');

      if (desc.includes('invalid') || desc.includes('size')) {
        this.clearScripts(scenario);
        stepNumber = 1;
        this.addScript(scenario, stepNumber++, 'Navigate to upload page', 'Open browser to upload URL', 'Upload page is displayed', '');
        this.addScript(scenario, stepNumber++, 'Select invalid file type', this.getTestData('fileUpload', 'invalid'), 'File is selected', '');
        this.addScript(scenario, stepNumber++, 'Click upload button', 'Click on "Upload" button', 'Validation error for file type', '');
        this.addScript(scenario, stepNumber++, 'Verify error message', 'Error: "Invalid file type"', 'File not uploaded', '');
      }
    } else {
      this.addScript(scenario, stepNumber++, 'Navigate to feature page', 'Open browser to relevant URL', 'Feature page is displayed', '');
      this.addScript(scenario, stepNumber++, 'Perform primary action', 'Execute the primary action', 'Action completes successfully', '');
      this.addScript(scenario, stepNumber++, 'Verify expected behavior', 'Expected system response', 'System behaves as expected', '');
      this.addScript(scenario, stepNumber++, 'Verify no errors', 'No error messages displayed', 'System remains stable', '');
    }
  }

  private addScript(
    scenario: TestScenario,
    stepNumber: number,
    action: string,
    testData: string,
    expectedResult: string,
    actualResult: string
  ): void {
    this.scripts.push({
      id: scenario.id,
      scenarioId: scenario.id,
      requirementId: scenario.requirementId,
      stepNumber,
      action,
      testData,
      expectedResult,
      actualResult,
      status: ExecutionStatus.NOT_EXECUTED,
    });
  }

  private clearScripts(scenario: TestScenario): void {
    this.scripts = this.scripts.filter(s => s.scenarioId !== scenario.id);
  }

  private getTestData(field: string, category: string): string {
    const td = this.testData.find(d => d.field === field);
    if (!td) return '<test_data>';

    switch (category) {
      case 'valid':
        return td.validData[Math.floor(Math.random() * td.validData.length)];
      case 'invalid':
        return td.invalidData[Math.floor(Math.random() * td.invalidData.length)];
      case 'boundary':
        return td.boundaryData[Math.floor(Math.random() * td.boundaryData.length)];
      case 'special':
        return td.specialCharacters[Math.floor(Math.random() * td.specialCharacters.length)];
      case 'sql':
        return td.sqlInjection[Math.floor(Math.random() * td.sqlInjection.length)];
      case 'xss':
        return td.xssInputs[Math.floor(Math.random() * td.xssInputs.length)];
      case 'null':
        return td.nullValue;
      case 'empty':
        return td.emptyValue;
      default:
        return td.validData[0];
    }
  }
}

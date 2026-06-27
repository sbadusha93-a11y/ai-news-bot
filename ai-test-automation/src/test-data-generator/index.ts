import { TestData } from '../types';
import { logger } from '../utils/logger';
import * as fs from 'fs-extra';
import * as path from 'path';

export class TestDataGenerator {
  private testData: TestData[] = [];

  generate(): TestData[] {
    logger.info('Generating comprehensive test data...');

    this.testData = [
      {
        field: 'username',
        validData: ['admin@test.com', 'user@example.com', 'john.doe@company.org', 'test_user123@domain.com', 'alice.smith@business.io'],
        invalidData: ['invalid-email', 'user@.com', '@domain.com', 'user@domain', 'plainaddress', 'user name@test', 'user@test..com'],
        boundaryData: ['a@b.co', 'a'.repeat(254) + '@test.com', 'ab@cd.ef', 'test@test.c'],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['user@test.com<script>', 'user name@test.com', 'user@te#st.com', 'user@te$st.com', 'user"test@test.com'],
        sqlInjection: ["' OR '1'='1", "admin'--", "'; DROP TABLE users; --", "' UNION SELECT * FROM users--", "1; SELECT * FROM users"],
        xssInputs: ['<script>alert(1)</script>', '<img src=x onerror=alert(1)>', '"><script>alert(1)</script>', '<svg onload=alert(1)>'],
      },
      {
        field: 'password',
        validData: ['P@ssw0rd123', 'Str0ng!Pass', 'Test@12345', 'Secure#Pass1', 'Compl3x!Pass', 'ValidP@ss1'],
        invalidData: ['weak', '12345', 'password', 'abc', 'short', 'P@ss1', 'n0spec@l'],
        boundaryData: ['A1@' + 'b'.repeat(5), 'A1@' + 'b'.repeat(128), 'A1@' + 'b'.repeat(7), 'A1@' + 'b'.repeat(64)],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['P@ssw0rd<script>', 'Pass"word', "Pass'word", 'Pass<word>', 'Pass&word'],
        sqlInjection: ["' OR 1=1--", "password' OR '1'='1", "'; EXEC xp_cmdshell--", "' UNION SELECT NULL--"],
        xssInputs: ['<script>alert("pwd")</script>', '"/><script>alert(1)</script>', '<img src=x onerror=alert(1)>'],
      },
      {
        field: 'email',
        validData: ['test@example.com', 'user.name+tag@domain.co.uk', 'user-name@domain.org', 'user@domain.io', 'first.last@company.com'],
        invalidData: ['not-an-email', 'missing@dot', '@nodomain.com', 'spaces in@email.com', 'user@.com', 'user@domain..com', ''],
        boundaryData: ['a@b.com', 'a'.repeat(254) + '@test.com', 'test@test.c', 'very.long.email.address@example.com'],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['test@<script>', 'test@domain.com<script>', 'test@domain.">', 'test"email@test.com'],
        sqlInjection: ["' OR 1=1--@test.com", "admin'--@test.com", "'; DROP TABLE--@test.com"],
        xssInputs: ['<script>alert("xss")</script>@test.com', 'test@<img src=x onerror=alert(1)>.com', '"><script>@test.com'],
      },
      {
        field: 'searchQuery',
        validData: ['laptop', 'wireless mouse', 'USB-C hub adapter', 'ergonomic keyboard', '4K monitor 27 inch'],
        invalidData: ['', '   ', '!@#$%^&*()', 'a', null as unknown as string],
        boundaryData: ['a', 'a'.repeat(500), 'ab', 'a'.repeat(1000)],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['<script>', 'DROP TABLE', 'OR 1=1', '%%%', '___', '[]'],
        sqlInjection: ["' OR 'x'='x", "'; SELECT * FROM products--", "' UNION SELECT NULL--", "1; DROP TABLE products"],
        xssInputs: ['<script>alert("search")</script>', '<svg onload=alert(1)>', '"><img src=x>', '<iframe src=javascript:alert(1)>'],
      },
      {
        field: 'phoneNumber',
        validData: ['+1234567890', '123-456-7890', '(123) 456-7890', '1234567890', '+1 (234) 567-8900', '123.456.7890'],
        invalidData: ['abc', '123', '+123', '1234567890123456', '12-34-56', 'phone', '123-456-789'],
        boundaryData: ['123456789', '123456789012345', '1111111111', '9999999999'],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['123-456-7890<script>', '123-456-<script>7890', '123-456-789"', "123-456-'7890"],
        sqlInjection: ["' OR 1=1--", "' DROP TABLE--", "'; EXEC--"],
        xssInputs: ['<script>alert("phone")</script>', '123<img src=x onerror=alert(1)>', '"><svg>'],
      },
      {
        field: 'amount',
        validData: ['100', '0.01', '999999.99', '50.00', '1000', '100.50', '0.00'],
        invalidData: ['-100', 'abc', '0', '100.001', '999999999.99', '-0.01', '10,000.00'],
        boundaryData: ['0.01', '999999.99', '0.00', '1000000.00', '-0.01', '1000000.01'],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['$100', '10,000', '<script>100', '100<script>', '100.00<script>'],
        sqlInjection: ["' OR '1'='1", "'; UPDATE balance--", "' UNION SELECT 100--"],
        xssInputs: ['<script>alert("amount")</script>', '100<img src=x>', '"><script>100'],
      },
      {
        field: 'date',
        validData: ['2024-01-15', '01/15/2024', '2024-12-31', '2024-02-29', '2024-06-15', '2024/01/15'],
        invalidData: ['13/01/2024', '2024-13-01', 'abcd', '2024/02/30', 'not-a-date', '02/30/2024', '2024/00/01'],
        boundaryData: ['1900-01-01', '2100-12-31', '2024-01-01', '2024-12-31', '0001-01-01', '9999-12-31'],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['<script>01/15/2024</script>', "01/15/'2024", '01/15/2024<script>'],
        sqlInjection: ["' OR '1'='1--", "'; DELETE FROM dates--", "' UNION SELECT GETDATE()--"],
        xssInputs: ['<script>alert("date")</script>', '01/15/<img src=x>', '"><script>2024'],
      },
      {
        field: 'fileUpload',
        validData: ['document.pdf', 'image.jpg', 'spreadsheet.xlsx', 'archive.zip', 'presentation.pptx', 'data.csv'],
        invalidData: ['virus.exe', 'script.bat', 'malware.sh', 'index.html', 'exploit.php', 'payload.js'],
        boundaryData: ['1KB_file.txt', '10MB_file.pdf', '0KB_empty.txt', '100MB_large_file.zip'],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['<script>.pdf', 'file".pdf', "file'.pdf", 'file<>.pdf', 'file|.pdf'],
        sqlInjection: ["'.sql", "'; DROP TABLE.sql", "' UNION SELECT.sql"],
        xssInputs: ['<script>alert("file")</script>.pdf', 'file.svg', 'file.html', '"><script>.pdf'],
      },
      {
        field: 'address',
        validData: ['123 Main St, New York, NY 10001', '456 Oak Avenue, Suite 200, Los Angeles, CA 90001', '789 Pine Road, Chicago, IL 60601'],
        invalidData: ['', '  ', '#$%^&*()', '', 'A'],
        boundaryData: ['A', 'A'.repeat(500), 'AB', 'A'.repeat(1000)],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['123 <script>Main St', '456 Oak Avenue"><script>', '789 Pine<script>Road'],
        sqlInjection: ["' OR '1'='1", "'; DROP TABLE addresses--", "' UNION SELECT * FROM addresses--"],
        xssInputs: ['<script>alert("address")</script>', '<img src=x onerror=alert(1)> Street', '"><svg onload=alert(1)>'],
      },
      {
        field: 'creditCard',
        validData: ['4111111111111111', '5500000000000004', '340000000000009', '6011000000000004', '3530111333300000'],
        invalidData: ['1234567890123456', '1111111111111111', 'abc', '4111111111111', '', '0000000000000000', '9999999999999999'],
        boundaryData: ['4111111111111111', '4111111111111112', '4000000000000000', '4999999999999999'],
        nullValue: '',
        emptyValue: '',
        specialCharacters: ['4111-1111-1111-1111<script>', '4111<script>1111', '4111-1111<script>'],
        sqlInjection: ["' OR '1'='1", "'; SELECT * FROM cards--", "' UNION SELECT credit_cards--"],
        xssInputs: ['<script>alert("cc")</script>', '4111<img src=x>1111', '"><script>4111'],
      },
    ];

    logger.info(`Generated test data for ${this.testData.length} fields`);
    return this.testData;
  }

  async saveToJson(outputDir: string): Promise<void> {
    const filePath = path.join(outputDir, 'testdata.json');
    await fs.ensureDir(outputDir);
    await fs.writeJson(filePath, this.testData, { spaces: 2 });
    logger.info(`Test data saved to: ${filePath}`);
  }

  async saveToExcel(outputDir: string): Promise<void> {
    const XLSX = require('xlsx');
    const filePath = path.join(outputDir, 'testdata.xlsx');

    const workbook = XLSX.utils.book_new();

    for (const td of this.testData) {
      const maxLen = Math.max(
        td.validData.length,
        td.invalidData.length,
        td.boundaryData.length,
        td.specialCharacters.length,
        td.sqlInjection.length,
        td.xssInputs.length,
        1
      );

      const rows: Record<string, string>[] = [];
      for (let i = 0; i < maxLen; i++) {
        rows.push({
          'Field': td.field,
          'Valid Data': td.validData[i] || '',
          'Invalid Data': td.invalidData[i] || '',
          'Boundary Data': td.boundaryData[i] || '',
          'Null Value': td.nullValue,
          'Empty Value': td.emptyValue,
          'Special Characters': td.specialCharacters[i] || '',
          'SQL Injection': td.sqlInjection[i] || '',
          'XSS Inputs': td.xssInputs[i] || '',
        });
      }

      const ws = XLSX.utils.json_to_sheet(rows);
      XLSX.utils.book_append_sheet(workbook, ws, td.field.substring(0, 31));
    }

    const summaryRows: Record<string, string>[] = [];
    for (const td of this.testData) {
      summaryRows.push({
        'Field': td.field,
        'Valid Count': String(td.validData.length),
        'Invalid Count': String(td.invalidData.length),
        'Boundary Count': String(td.boundaryData.length),
        'Special Char Count': String(td.specialCharacters.length),
        'SQL Injection Count': String(td.sqlInjection.length),
        'XSS Count': String(td.xssInputs.length),
      });
    }
    const summaryWs = XLSX.utils.json_to_sheet(summaryRows);
    XLSX.utils.book_append_sheet(workbook, summaryWs, 'Summary');

    await fs.ensureDir(outputDir);
    XLSX.writeFile(workbook, filePath);
    logger.info(`Test data Excel saved to: ${filePath}`);
  }
}

import * as fs from 'fs-extra';
import * as path from 'path';

export class TestDataUtil {
  private data: Record<string, any> = {};

  constructor(dataDir?: string) {
    const dir = dataDir || path.join(process.cwd(), 'test-data');
    this.loadFromJson(dir);
  }

  private loadFromJson(dir: string): void {
    const jsonPath = path.join(dir, 'testdata.json');
    if (fs.existsSync(jsonPath)) {
      this.data = fs.readJsonSync(jsonPath);
    }
  }

  getValidData(field: string): string {
    const fieldData = this.data[field];
    if (fieldData?.validData?.length > 0) {
      return fieldData.validData[0];
    }
    return 'test_data';
  }

  getInvalidData(field: string): string {
    const fieldData = this.data[field];
    if (fieldData?.invalidData?.length > 0) {
      return fieldData.invalidData[0];
    }
    return 'invalid';
  }

  getBoundaryData(field: string): string {
    const fieldData = this.data[field];
    if (fieldData?.boundaryData?.length > 0) {
      return fieldData.boundaryData[0];
    }
    return '';
  }

  getSecurityPayload(field: string, type: 'sql' | 'xss'): string {
    const fieldData = this.data[field];
    if (fieldData && fieldData[type + 'Inputs']?.length > 0) {
      return fieldData[type + 'Inputs'][0];
    }
    return type === 'sql' ? "' OR '1'='1" : '<script>alert(1)</script>';
  }

  getRandomValid(field: string): string {
    const fieldData = this.data[field];
    if (fieldData?.validData?.length > 0) {
      const arr = fieldData.validData;
      return arr[Math.floor(Math.random() * arr.length)];
    }
    return 'test_data';
  }
}

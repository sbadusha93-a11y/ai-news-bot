import * as fs from 'fs-extra';
import * as path from 'path';
import { ParsedDocument, DocumentSection } from '../types';
import { logger } from '../utils/logger';

export class DocumentReader {
  private readonly filePath: string;
  private readonly extension: string;
  private readonly supportedFormats = ['.pdf', '.docx', '.txt', '.xlsx', '.xls', '.csv'];

  constructor(filePath: string) {
    this.filePath = path.resolve(filePath);
    this.extension = path.extname(this.filePath).toLowerCase();
    this.validate();
  }

  private validate(): void {
    if (!fs.existsSync(this.filePath)) {
      throw new Error(`File not found: ${this.filePath}`);
    }
    if (!this.supportedFormats.includes(this.extension)) {
      throw new Error(
        `Unsupported format: ${this.extension}. Supported: ${this.supportedFormats.join(', ')}`
      );
    }
  }

  async read(): Promise<ParsedDocument> {
    logger.info(`Reading document: ${this.filePath}`);
    switch (this.extension) {
      case '.pdf':
        return this.readPdf();
      case '.docx':
        return this.readDocx();
      case '.txt':
        return this.readTxt();
      case '.xlsx':
      case '.xls':
        return this.readXlsx();
      case '.csv':
        return this.readCsv();
      default:
        throw new Error(`Unsupported format: ${this.extension}`);
    }
  }

  private async readPdf(): Promise<ParsedDocument> {
    try {
      const pdfParse = require('pdf-parse');
      const dataBuffer = await fs.readFile(this.filePath);
      const data = await pdfParse(dataBuffer);
      const sections: DocumentSection[] = [];

      const pages = data.text.split('\n\n').filter((p: string) => p.trim());
      pages.forEach((pageText: string, i: number) => {
        sections.push({
          style: 'Page',
          text: pageText.trim(),
          data: [{ page: i + 1 }],
        });
      });

      return {
        text: data.text,
        sections,
        metadata: {
          pages: data.numpages,
          title: data.info?.Title || '',
          author: data.info?.Author || '',
          producer: data.info?.Producer || '',
        },
        format: 'pdf',
      };
    } catch (error) {
      logger.error(`Error reading PDF: ${(error as Error).message}`);
      throw error;
    }
  }

  private async readDocx(): Promise<ParsedDocument> {
    try {
      const mammoth = require('mammoth');
      const buffer = await fs.readFile(this.filePath);
      const result = await mammoth.extractRawText({ buffer });
      const text = result.value || '';
      const lines = text.split('\n').filter((l: string) => l.trim());
      const sections: DocumentSection[] = [];

      let currentHeader = '';
      let currentText: string[] = [];

      for (const line of lines) {
        const trimmed = line.trim();
        if (
          trimmed === trimmed.toUpperCase() &&
          trimmed.length > 3 &&
          trimmed.length < 100
        ) {
          if (currentText.length > 0) {
            sections.push({
              style: 'Section',
              text: currentText.join('\n'),
              header: currentHeader,
            });
            currentText = [];
          }
          currentHeader = trimmed;
        } else {
          currentText.push(line);
        }
      }

      if (currentText.length > 0) {
        sections.push({
          style: 'Section',
          text: currentText.join('\n'),
          header: currentHeader,
        });
      }

      return {
        text,
        sections,
        metadata: {
          warnings: result.messages,
          paragraphs: lines.length,
        },
        format: 'docx',
      };
    } catch (error) {
      logger.error(`Error reading DOCX: ${(error as Error).message}`);
      throw error;
    }
  }

  private async readTxt(): Promise<ParsedDocument> {
    try {
      const content = await fs.readFile(this.filePath, 'utf-8');
      const lines = content.split('\n');
      const sections: DocumentSection[] = [];

      let currentHeader = '';
      let currentText: string[] = [];

      for (const line of lines) {
        const trimmed = line.trim();
        if (
          (trimmed.endsWith(':') || trimmed.startsWith('#')) &&
          trimmed.length < 100
        ) {
          if (currentText.length > 0) {
            sections.push({
              style: 'Section',
              text: currentText.join('\n'),
              header: currentHeader,
            });
            currentText = [];
          }
          currentHeader = trimmed.replace(/^#+\s*/, '');
        } else {
          currentText.push(line);
        }
      }

      if (currentText.length > 0) {
        sections.push({
          style: 'Section',
          text: currentText.join('\n'),
          header: currentHeader,
        });
      }

      return {
        text: content,
        sections,
        metadata: {
          lines: lines.length,
          characters: content.length,
        },
        format: 'txt',
      };
    } catch (error) {
      logger.error(`Error reading TXT: ${(error as Error).message}`);
      throw error;
    }
  }

  private async readXlsx(): Promise<ParsedDocument> {
    try {
      const XLSX = require('xlsx');
      const workbook = XLSX.readFile(this.filePath);
      const sections: DocumentSection[] = [];
      const fullText: string[] = [];

      for (const sheetName of workbook.SheetNames) {
        const worksheet = workbook.Sheets[sheetName];
        const data = XLSX.utils.sheet_to_json(worksheet, { defval: '' });
        const text = data
          .map((row: Record<string, unknown>) =>
            Object.values(row).join(' | ')
          )
          .join('\n');

        fullText.push(`=== Sheet: ${sheetName} ===\n${text}`);
        sections.push({
          style: 'Sheet',
          sheetName,
          text,
          data: data as Record<string, unknown>[],
          columns: data.length > 0 ? Object.keys(data[0]) : [],
          rows: data.length,
        });
      }

      return {
        text: fullText.join('\n\n'),
        sections,
        metadata: {
          sheets: workbook.SheetNames.length,
          sheetNames: workbook.SheetNames,
        },
        format: 'xlsx',
      };
    } catch (error) {
      logger.error(`Error reading XLSX: ${(error as Error).message}`);
      throw error;
    }
  }

  private async readCsv(): Promise<ParsedDocument> {
    try {
      const content = await fs.readFile(this.filePath, 'utf-8');
      const lines = content.split('\n').filter((l: string) => l.trim());
      const headers = lines[0].split(',').map((h: string) => h.trim());
      const data = lines.slice(1).map((line: string) => {
        const values = line.split(',').map((v: string) => v.trim());
        const row: Record<string, unknown> = {};
        headers.forEach((header: string, i: number) => {
          row[header] = values[i] || '';
        });
        return row;
      });

      return {
        text: content,
        sections: [
          {
            style: 'CSV',
            text: content,
            data,
            columns: headers,
            rows: data.length,
          },
        ],
        metadata: {
          columns: headers,
          rows: data.length,
        },
        format: 'csv',
      };
    } catch (error) {
      logger.error(`Error reading CSV: ${(error as Error).message}`);
      throw error;
    }
  }
}

export async function readDocument(filePath: string): Promise<ParsedDocument> {
  const reader = new DocumentReader(filePath);
  return reader.read();
}

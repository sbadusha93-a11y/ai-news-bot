import * as fs from 'fs-extra';
import * as path from 'path';

export class LoggerUtil {
  private logDir: string;
  private logFile: string;

  constructor(logDir?: string) {
    this.logDir = logDir || path.join(process.cwd(), 'logs');
    fs.ensureDirSync(this.logDir);
    this.logFile = path.join(this.logDir, `execution-${Date.now()}.log`);
  }

  private timestamp(): string {
    return new Date().toISOString();
  }

  private write(level: string, message: string): void {
    const line = `[${this.timestamp()}] [${level}] ${message}\n`;
    console.log(line.trim());
    fs.appendFileSync(this.logFile, line);
  }

  info(message: string): void { this.write('INFO', message); }
  warn(message: string): void { this.write('WARN', message); }
  error(message: string): void { this.write('ERROR', message); }
  debug(message: string): void {
    if (process.env.DEBUG) { this.write('DEBUG', message); }
  }
}

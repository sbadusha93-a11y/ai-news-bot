export class Logger {
  private context: string;

  constructor(context: string) {
    this.context = context;
  }

  private timestamp(): string {
    return new Date().toISOString();
  }

  info(message: string): void {
    console.log(`[${this.timestamp()}] [INFO] [${this.context}] ${message}`);
  }

  warn(message: string): void {
    console.warn(`[${this.timestamp()}] [WARN] [${this.context}] ${message}`);
  }

  error(message: string): void {
    console.error(`[${this.timestamp()}] [ERROR] [${this.context}] ${message}`);
  }

  debug(message: string): void {
    if (process.env.LOG_LEVEL === 'debug') {
      console.debug(`[${this.timestamp()}] [DEBUG] [${this.context}] ${message}`);
    }
  }
}

export const logger = new Logger('AI-Test-Automation');

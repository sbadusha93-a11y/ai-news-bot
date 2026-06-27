import { FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig): Promise<void> {
  console.log('Global setup: Initializing test environment...');
}

export default globalSetup;

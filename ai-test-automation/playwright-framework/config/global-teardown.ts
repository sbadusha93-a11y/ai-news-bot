import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig): Promise<void> {
  console.log('Global teardown: Cleaning up test environment...');
}

export default globalTeardown;

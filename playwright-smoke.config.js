import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './playwright-tests',
  timeout: 30_000,
  expect: {
    timeout: 10_000
  },
  use: {
    baseURL: 'https://sweeden-ttu.github.io/legal-luminary/',
    trace: 'on-first-retry'
  },
  reporter: [['list']]
});

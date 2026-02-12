import { test, expect } from '@playwright/test';

test.describe('LangSmith+LangGraph demo placeholder', () => {
  test('demo folder should be reachable on dev server', async ({ request }) => {
    const base = process.env.PLAYWRIGHT_BASE_URL ?? 'http://127.0.0.1:4000';
    const url = new URL('/demos/langsmith_langgraph_demo/', base).toString();
    const res = await request.get(url);
    expect(res.status()).toBeGreaterThanOrEqual(200);
  });
});

import { test, expect } from '@playwright/test';
import { ensureAuthenticated } from './auth_helper';

test.describe('VEID Enterprise - Authentication & Central Console', () => {
  test.setTimeout(120000);

  test('User can log in and see Carbone navbar & Bento App Drawer without JS crashes', async ({ page }) => {
    // Collect uncaught console errors
    const uncaughtErrors: string[] = [];
    page.on('pageerror', err => uncaughtErrors.push(err.message));

    // 1. Authenticate via robust helper
    await ensureAuthenticated(page);

    // 2. Wait for navbar to mount and be visible in backend
    const navbar = page.locator('.o_main_navbar');
    await expect(navbar).toBeVisible({ timeout: 35000 });

    // 3. Verify Navbar styling (Carbone #081323 = rgb(8, 19, 35))
    const bgColor = await navbar.evaluate(el => window.getComputedStyle(el).backgroundColor);
    expect(bgColor).toMatch(/rgb\(8,\s*19,\s*35\)/);

    // 4. Verify Left Rail Navigation and Navbar Apps button
    const sidebar = page.locator('#veid-enterprise-sidebar, .veid-app-sidebar');
    await expect(sidebar.first()).toBeVisible({ timeout: 25000 });

    const appsBtn = page.locator('#veid-header-apps-btn');
    await expect(appsBtn).toBeVisible({ timeout: 15000 });

    // 5. Ensure zero critical JavaScript crash errors
    const criticalErrors = uncaughtErrors.filter(e => !e.includes('ResizeObserver') && !e.includes('favicon'));
    expect(criticalErrors).toHaveLength(0);
  });
});

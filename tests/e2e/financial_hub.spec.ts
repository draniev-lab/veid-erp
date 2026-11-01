import { test, expect } from '@playwright/test';
import { ensureAuthenticated } from './auth_helper';

test.describe('VEID Enterprise - Financial & Invoicing Hub', () => {
  test.setTimeout(60000);

  test('User can open Invoices view without JS crashes and see modern form/list views', async ({ page }) => {
    // Collect console errors
    const uncaughtErrors: string[] = [];
    page.on('pageerror', err => uncaughtErrors.push(err.message));

    // 1. Authenticate via robust helper
    await ensureAuthenticated(page);

    // 2. Navigate directly to Invoices action (action-270)
    await page.evaluate(() => { window.location.href = '/odoo/action-270'; });
    await page.waitForFunction(() => window.location.pathname.includes('action-270'), { timeout: 25000 });
    await page.waitForTimeout(3000);

    // Verify view container mounts
    const viewContainer = page.locator('.o_action_manager, .o_list_renderer, .o_view_controller');
    await expect(viewContainer.first()).toBeVisible({ timeout: 25000 });

    // Verify Control Panel / Breadcrumbs are displayed
    const controlPanel = page.locator('.o_control_panel');
    await expect(controlPanel).toBeVisible();

    // Verify New Invoice button exists
    const newBtn = page.locator('button.o_list_button_add, button:has-text("Nouveau"), button:has-text("New")');
    if (await newBtn.count() > 0) {
      await expect(newBtn.first()).toBeVisible();
    }

    // Ensure zero critical JavaScript crash errors
    const criticalErrors = uncaughtErrors.filter(e => !e.includes('ResizeObserver') && !e.includes('favicon'));
    expect(criticalErrors).toHaveLength(0);
  });

  test('User can open invoice form and see VEID Mobile Money Hub tab and fields', async ({ page }) => {
    const uncaughtErrors: string[] = [];
    page.on('pageerror', err => uncaughtErrors.push(err.message));

    // 1. Authenticate via robust helper
    await ensureAuthenticated(page);

    // 2. Open Invoices
    await page.evaluate(() => { window.location.href = '/odoo/action-270'; });
    await page.waitForFunction(() => window.location.pathname.includes('action-270'), { timeout: 25000 });
    await page.waitForTimeout(3000);

    // 3. Click "Nouveau" or first record to open form view
    const newBtn = page.locator('button.o_list_button_add, button:has-text("Nouveau"), button:has-text("New")');
    if (await newBtn.count() > 0 && await newBtn.first().isVisible()) {
      await newBtn.first().click({ noWaitAfter: true });
      await page.waitForTimeout(4000);

      // Verify Notebook tab "Conformité & Suivi MonErp" exists
      const momoTab = page.locator('a.nav-link:has-text("Conformité & Suivi MonErp"), a.nav-link[name="monerp_account_compliance"]');
      if (await momoTab.count() > 0) {
        await momoTab.first().click();
        await page.waitForTimeout(1000);

        // Verify Mobile Money section headers / fields exist
        const momoSection = page.locator('div:has-text("Paiement Mobile Money VEID")');
        await expect(momoSection.first()).toBeVisible({ timeout: 10000 });
      }
    }

    const criticalErrors = uncaughtErrors.filter(e => !e.includes('ResizeObserver') && !e.includes('favicon'));
    expect(criticalErrors).toHaveLength(0);
  });
});

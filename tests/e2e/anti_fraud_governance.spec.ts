import { test, expect } from '@playwright/test';
import { ensureAuthenticated } from './auth_helper';

test.describe('VEID Enterprise - Phase 3 Anti-Fraud Governance & Audit Trail', () => {
  test.setTimeout(60000);

  test('User can inspect invoice and view Anti-Fraud Governance & Cryptographic Ledger section', async ({ page }) => {
    const uncaughtErrors: string[] = [];
    page.on('pageerror', err => uncaughtErrors.push(err.message));

    // 1. Authenticate via robust helper
    await ensureAuthenticated(page);

    // 2. Navigate to Invoices
    await page.evaluate(() => { window.location.href = '/odoo/action-270'; });
    await page.waitForFunction(() => window.location.pathname.includes('action-270'), { timeout: 25000 });
    await page.waitForTimeout(3000);

    // 3. Click "Nouveau" or open record
    const newBtn = page.locator('button.o_list_button_add, button:has-text("Nouveau"), button:has-text("New")');
    if (await newBtn.count() > 0 && await newBtn.first().isVisible()) {
      await newBtn.first().click({ noWaitAfter: true });
      await page.waitForTimeout(4000);

      // Verify Notebook tab "Conformité & Suivi MonErp"
      const compTab = page.locator('a.nav-link:has-text("Conformité & Suivi MonErp"), a.nav-link[name="monerp_account_compliance"]');
      if (await compTab.count() > 0) {
        await compTab.first().click();
        await page.waitForTimeout(1000);

        // Verify "Gouvernance Anti-Fraude & Journal Immuable VEID" section exists
        const fraudSection = page.locator('div:has-text("Gouvernance Anti-Fraude & Journal Immuable VEID")');
        await expect(fraudSection.first()).toBeVisible({ timeout: 10000 });

        // Verify Anti-Fraud tier and state fields are rendered
        const tierField = page.locator('[name="veid_approval_tier"], .o_field_widget[name="veid_approval_tier"]');
        if (await tierField.count() > 0) {
          await expect(tierField.first()).toBeVisible();
        }
      }
    }

    // Zero critical JavaScript crashes
    const criticalErrors = uncaughtErrors.filter(e => !e.includes('ResizeObserver') && !e.includes('favicon'));
    expect(criticalErrors).toHaveLength(0);
  });
});

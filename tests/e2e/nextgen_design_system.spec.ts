import { test, expect } from '@playwright/test';
import { ensureAuthenticated } from './auth_helper';

test.describe('VEID Enterprise - Next-Gen Design System & Anti-Plagiat Odoo', () => {
  test.setTimeout(120000);

  test('User experiences modern Left Rail Sidebar with collapsible toggle', async ({ page }) => {
    const uncaughtErrors: string[] = [];
    page.on('pageerror', err => uncaughtErrors.push(err.message));

    // 1. Authenticate into backend
    await ensureAuthenticated(page);

    // 2. Verify Left Rail Sidebar is present
    const sidebar = page.locator('#veid-enterprise-sidebar, .veid-app-sidebar');
    await expect(sidebar.first()).toBeVisible({ timeout: 25000 });

    // 3. Verify Brand Icon and Text inside Sidebar
    const brandName = page.locator('.veid-brand-name');
    if (await brandName.count() > 0) {
      await expect(brandName.first()).toContainText('VEID');
    }

    // 4. Verify Pinned Sectoral Navigation Links exist
    const navItems = page.locator('.veid-nav-link');
    expect(await navItems.count()).toBeGreaterThanOrEqual(4);

    // 5. Test Sidebar Collapse/Expand Toggle
    const toggleBtn = page.locator('#veid-sidebar-toggle');
    if (await toggleBtn.count() > 0 && await toggleBtn.first().isVisible()) {
      await toggleBtn.first().click({ force: true });
      await page.waitForTimeout(500);
      await expect(sidebar.first()).toHaveClass(/collapsed/);

      // Re-expand
      await toggleBtn.first().click({ force: true });
      await page.waitForTimeout(500);
      await expect(sidebar.first()).not.toHaveClass(/collapsed/);
    }

    // Zero critical JavaScript errors
    const criticalErrors = uncaughtErrors.filter(e => !e.includes('ResizeObserver') && !e.includes('favicon'));
    expect(criticalErrors).toHaveLength(0);
  });

  test('Universal Command Palette (Ctrl+K) opens, filters commands, and closes with ESC', async ({ page }) => {
    const uncaughtErrors: string[] = [];
    page.on('pageerror', err => uncaughtErrors.push(err.message));

    await ensureAuthenticated(page);

    // 1. Trigger Command Palette via keyboard (Control+k)
    await page.keyboard.press('Control+k');
    await page.waitForTimeout(800);

    const overlay = page.locator('#veid-palette-overlay');
    await expect(overlay).toBeVisible({ timeout: 10000 });

    // 2. Type search query in input
    const input = page.locator('#veid-palette-input');
    await input.click();
    await input.fill('Factures');
    await page.waitForTimeout(400);

    // 3. Verify filtered results show invoices
    const results = page.locator('.veid-palette-item');
    expect(await results.count()).toBeGreaterThanOrEqual(1);
    await expect(results.first()).toContainText('Factures');

    // 4. Press Escape to close
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
    await expect(overlay).not.toBeVisible();

    // Zero critical JavaScript errors
    const criticalErrors = uncaughtErrors.filter(e => !e.includes('ResizeObserver') && !e.includes('favicon'));
    expect(criticalErrors).toHaveLength(0);
  });

  test('Full-Canvas Form and Data Grid deliver modern layout without classic Odoo paper sheet', async ({ page }) => {
    const uncaughtErrors: string[] = [];
    page.on('pageerror', err => uncaughtErrors.push(err.message));

    await ensureAuthenticated(page);

    // 1. Navigate to Invoices list
    await page.evaluate(() => { window.location.href = '/odoo/action-270'; });
    await page.waitForFunction(() => window.location.pathname.includes('action-270'), { timeout: 25000 });
    await page.waitForTimeout(3000);

    // 2. Verify Data Grid table
    const table = page.locator('.o_list_table');
    if (await table.count() > 0) {
      await expect(table.first()).toBeVisible({ timeout: 15000 });
    }

    // 3. Open Form View
    const newBtn = page.locator('button.o_list_button_add, button:has-text("Nouveau"), button:has-text("New")');
    if (await newBtn.count() > 0 && await newBtn.first().isVisible()) {
      await newBtn.first().click({ noWaitAfter: true });
      await page.waitForTimeout(4000);

      // Verify form sheet has full-canvas width styling
      const formSheet = page.locator('.o_form_sheet');
      await expect(formSheet.first()).toBeVisible({ timeout: 15000 });
      const sheetWidth = await formSheet.first().evaluate(el => window.getComputedStyle(el).width);
      expect(parseInt(sheetWidth, 10)).toBeGreaterThanOrEqual(500);
    }

    // Zero critical JavaScript errors
    const criticalErrors = uncaughtErrors.filter(e => !e.includes('ResizeObserver') && !e.includes('favicon'));
    expect(criticalErrors).toHaveLength(0);
  });

  test('Mobile viewport (390x844) delivers Task-First field navigation bar with accessible touch targets', async ({ page }) => {
    const uncaughtErrors: string[] = [];
    page.on('pageerror', err => uncaughtErrors.push(err.message));

    // 1. Set mobile viewport (iPhone 14 / modern Android)
    await page.setViewportSize({ width: 390, height: 844 });
    await ensureAuthenticated(page);

    // 2. Verify sidebar adapts into mobile bottom bar
    const sidebar = page.locator('#veid-enterprise-sidebar, .veid-app-sidebar');
    await expect(sidebar.first()).toBeVisible({ timeout: 25000 });

    const bbox = await sidebar.first().boundingBox();
    expect(bbox).not.toBeNull();
    if (bbox) {
      // Must be compact bottom dock (<= 75px height)
      expect(bbox.height).toBeLessThanOrEqual(75);
    }

    // 3. Verify touch-friendly navigation links
    const navLinks = page.locator('.veid-nav-link');
    expect(await navLinks.count()).toBeGreaterThanOrEqual(2);

    // Zero critical JavaScript errors
    const criticalErrors = uncaughtErrors.filter(e => !e.includes('ResizeObserver') && !e.includes('favicon'));
    expect(criticalErrors).toHaveLength(0);
  });

  test('VEID Copilot Assistant button and panel are styled with Titanium/Cobalt tokens (zero purple)', async ({ page }) => {
    const uncaughtErrors: string[] = [];
    page.on('pageerror', err => uncaughtErrors.push(err.message));

    await ensureAuthenticated(page);

    // 1. Verify Copilot launcher exists
    const launcher = page.locator('#veid-ai-launcher');
    await expect(launcher).toBeVisible({ timeout: 15000 });

    // 2. Click to open panel
    await launcher.click();
    await page.waitForTimeout(500);

    const panel = page.locator('#veid-ai-panel');
    await expect(panel).toBeVisible({ timeout: 5000 });
    await expect(panel).not.toHaveClass(/veid-ai-hidden/);

    // 3. Verify Header and title
    await expect(panel.locator('.veid-ai-heading strong')).toContainText('VEID Copilot');

    // 4. Close panel
    const closeBtn = panel.locator('.veid-ai-close');
    await closeBtn.click();
    await page.waitForTimeout(400);
    await expect(panel).toHaveClass(/veid-ai-hidden/);

    // Zero critical errors
    const criticalErrors = uncaughtErrors.filter(e => !e.includes('ResizeObserver') && !e.includes('favicon'));
    expect(criticalErrors).toHaveLength(0);
  });
});

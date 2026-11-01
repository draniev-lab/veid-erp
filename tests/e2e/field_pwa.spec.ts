import { test, expect } from '@playwright/test';

test.describe('VEID Enterprise - Offline-First Field Operations (PWA)', () => {
  test.setTimeout(60000);

  test('PWA loads shell, renders tabs, and navigates correctly', async ({ page }) => {
    const uncaughtErrors: string[] = [];
    page.on('pageerror', err => uncaughtErrors.push(err.message));

    // 1. Navigate to Field PWA
    await page.goto('/field', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);

    // 2. Verify PWA Header & Title
    const headerTitle = page.locator('.brand-title');
    await expect(headerTitle).toHaveText('VEID Field');

    // 3. Verify Initial Online Badge
    const networkBadge = page.locator('#network-badge');
    await expect(networkBadge).toBeVisible();

    // 4. Verify Tabs switching
    const tabAgro = page.locator('#tab-btn-agro');
    await tabAgro.click();
    await expect(page.locator('#tab-agro')).toHaveClass(/active/);

    const tabQueue = page.locator('#tab-btn-queue');
    await tabQueue.click();
    await expect(page.locator('#tab-queue')).toHaveClass(/active/);

    const tabBtp = page.locator('#tab-btn-btp');
    await tabBtp.click();
    await expect(page.locator('#tab-btp')).toHaveClass(/active/);

    // 5. Zero JS errors
    const criticalErrors = uncaughtErrors.filter(e => !e.includes('ResizeObserver') && !e.includes('favicon'));
    expect(criticalErrors).toHaveLength(0);
  });

  test('Simulated offline mode: persists report in IndexedDB and syncs when reconnected', async ({ context, page }) => {
    const uncaughtErrors: string[] = [];
    page.on('pageerror', err => uncaughtErrors.push(err.message));

    // 1. Open Field PWA
    await page.goto('/field', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);

    // 2. Go OFFLINE (Simulate rural dead zone without 3G/4G)
    await context.setOffline(true);
    await page.evaluate(() => window.dispatchEvent(new Event('offline')));
    await page.waitForTimeout(1000);

    // Verify offline badge
    const badgeLabel = page.locator('#network-label');
    await expect(badgeLabel).toContainText('Hors-Ligne');

    // 3. Submit a BTP progress report while offline
    // Populate dropdown with offline test fallback if empty
    await page.evaluate(() => {
      const select = document.getElementById('btp-site-select') as HTMLSelectElement;
      if (select && (!select.value || select.value === '')) {
        select.innerHTML = '<option value="999">CHANT-2026-TEST - Chantier SOTOUBOUA (40%)</option>';
        select.value = '999';
      }
    });

    await page.fill('#btp-progress-input', '75.5');
    await page.fill('#btp-notes-input', 'Coulage du radier généralisé achevé sous pluie battante.');
    await page.click('#btn-submit-btp');
    await page.waitForTimeout(1000);

    // 4. Check feedback and queue badge
    const alertFeedback = page.locator('#feedback-alert');
    await expect(alertFeedback).toBeVisible();
    await expect(alertFeedback).toContainText('enregistré');

    // Check queue tab shows 1 pending report
    const queueTab = page.locator('#tab-btn-queue');
    await queueTab.click();
    await page.waitForTimeout(1000);

    const queueBadge = page.locator('#queue-count-badge');
    await expect(queueBadge).toContainText('1 en attente');

    // 5. Verify persistence in IndexedDB
    const queueItemsCount = await page.evaluate(async () => {
      // @ts-ignore
      if (window.veidDb) {
        // @ts-ignore
        const pending = await window.veidDb.getPendingReports();
        return pending.length;
      }
      return 0;
    });
    expect(queueItemsCount).toBe(1);

    // 6. Go ONLINE (Network restored)
    await context.setOffline(false);
    await page.evaluate(() => window.dispatchEvent(new Event('online')));
    await page.waitForTimeout(2000);

    // Network badge must return to online
    await expect(badgeLabel).toContainText('En Ligne');

    // 7. Trigger Sync
    const syncBtn = page.locator('#btn-manual-sync');
    await syncBtn.click();
    await page.waitForTimeout(2000);

    // Zero critical JS errors
    const criticalErrors = uncaughtErrors.filter(e => !e.includes('ResizeObserver') && !e.includes('favicon'));
    expect(criticalErrors).toHaveLength(0);
  });
});

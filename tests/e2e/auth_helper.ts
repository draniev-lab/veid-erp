import { Page, expect } from '@playwright/test';

/**
 * Ensures user is authenticated into VEID Enterprise before running protected tests.
 */
export async function ensureAuthenticated(page: Page) {
  // If already at backend (/odoo), nothing to do
  if (page.url().includes('/odoo')) {
    return;
  }

  await page.goto('/web/login', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);

  // In Odoo, visiting /web/login when already authenticated immediately redirects to /odoo
  if (page.url().includes('/odoo')) {
    return;
  }

  // Ensure login form is visible by removing any bootstrap d-none if Odoo JS delay occurs
  await page.evaluate(() => {
    document.querySelectorAll('.oe_login_form').forEach(el => el.classList.remove('d-none'));
  });

  const loginInput = page.locator('input[name="login"]');
  await loginInput.waitFor({ state: 'visible', timeout: 15000 });
  await loginInput.fill('veinardjosue@gmail.com');
  const passwordInput = page.locator('input[name="password"]');
  await passwordInput.fill('admin');

  // Submit login specifically within the login form and wait for redirect
  try {
    await Promise.all([
      page.waitForURL('**/odoo**', { timeout: 60000, waitUntil: 'domcontentloaded' }),
      page.locator('.oe_login_form button[type="submit"], .oe_login_form .btn-primary').first().click(),
    ]);
  } catch (err) {
    if (!page.url().includes('/odoo')) {
      try {
        await page.locator('.oe_login_form button[type="submit"], .oe_login_form .btn-primary').first().click({ force: true, timeout: 3000 });
      } catch (_) {}
      await page.waitForURL('**/odoo**', { timeout: 40000, waitUntil: 'domcontentloaded' });
    }
  }

  await page.waitForTimeout(3000);
}

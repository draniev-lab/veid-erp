import { test, expect } from '@playwright/test';

test.describe('VEID Enterprise - Branding & Anti-Plagiat Verification', () => {
  test('Login page renders with VEID branding and no Odoo traces in title or brand footer', async ({ page }) => {
    const response = await page.goto('/web/login', { waitUntil: 'domcontentloaded' });
    expect(response?.status()).toBe(200);

    // 1. Verify Page Title
    await expect(page).toHaveTitle(/VEID Enterprise/);

    // 2. Verify OpenGraph & Meta Tags
    const ogTitle = await page.locator('meta[property="og:title"]').getAttribute('content');
    expect(ogTitle).toContain('VEID Enterprise');

    // 3. Verify Favicon link
    const favicon = page.locator('link[rel="shortcut icon"]');
    await expect(favicon).toHaveCount(1);
    const faviconHref = await favicon.getAttribute('href');
    expect(faviconHref).toBeTruthy();

    if (faviconHref) {
      const favResponse = await page.request.get(faviconHref);
      expect(favResponse.status()).toBe(200);
      expect(favResponse.headers()['content-type']).toContain('image');
    }

    // 4. Verify Futuristic Logo is present and visible
    const logoImg = page.locator('img[src*="veid_logo_futuristic"]');
    await expect(logoImg).toBeVisible();

    // 5. Verify Brand Promotion text
    const brandPromo = page.locator('.o_brand_promotion');
    if (await brandPromo.count() > 0) {
      const text = await brandPromo.innerText();
      expect(text).toContain('VEID Enterprise');
      expect(text).not.toContain('Odoo.com');
    }

    // Verify no unhandled severe assets error
    const pageHtml = await page.content();
    expect(pageHtml).not.toContain('The style compilation failed');
    expect(pageHtml).not.toContain('error__odooAssetError');
  });
});

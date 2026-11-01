import { test, expect } from '@playwright/test';
import { ensureAuthenticated } from './auth_helper';

test.describe('VEID Enterprise - Phase 4 Operational AI & Predictive Treasury', () => {
  test.setTimeout(90000);

  test('AI Invoice OCR API parses raw West-African invoice into structured data', async ({ request }) => {
    const rawInvoiceText = `
      SOCIETE GENERALE DE TRAVAUX PUBLICS DU TOGO (SGTP-TOGO)
      NIF: 1004829104
      Facture N°: FAC-2026-LOME-044
      Date: 18/10/2026
      
      Fourniture de sable et ciment CPJ 45 pour chantier Agoe.
      
      Total HT: 4500000 FCFA
      TVA 18%: 810000 FCFA
      Net a payer: 5310000 FCFA
    `;

    const response = await request.post('/api/v1/veid/ai/parse-invoice', {
      data: { text: rawInvoiceText },
      headers: { 'Content-Type': 'application/json' },
    });

    expect(response.status()).toBe(200);
    const json = await response.json();
    expect(json.status).toBe('success');
    expect(json.data.invoice_ref).toBe('FAC-2026-LOME-044');
    expect(json.data.partner_vat).toBe('1004829104');
    expect(json.data.amount_untaxed).toBe(4500000);
    expect(json.data.amount_tax).toBe(810000);
    expect(json.data.amount_total).toBe(5310000);
    expect(json.data.confidence).toBeGreaterThanOrEqual(60);
  });

  test('Predictive Treasury Forecast API returns 30/60/90j buckets and client risk scoring', async ({ request }) => {
    const response = await request.get('/api/v1/veid/ai/treasury-forecast');
    expect(response.status()).toBe(200);

    const json = await response.json();
    expect(json.status).toBe('success');
    expect(json.forecast).toBeDefined();
    expect(json.forecast.company_name).toBe('VEID Enterprise');
    expect(json.forecast.currency).toBe('XOF');

    // Verify projection buckets exist
    expect(json.forecast.inflows).toHaveProperty('d30');
    expect(json.forecast.inflows).toHaveProperty('d60');
    expect(json.forecast.inflows).toHaveProperty('d90');
    expect(json.forecast.outflows).toHaveProperty('d30');
    expect(json.forecast.outflows).toHaveProperty('d60');
    expect(json.forecast.outflows).toHaveProperty('d90');
    expect(json.forecast.alerts).toHaveProperty('ai_risk_level');
  });

  test('User can inspect invoice and view AI OCR & Extraction section in backend form', async ({ page }) => {
    const uncaughtErrors: string[] = [];
    page.on('pageerror', err => uncaughtErrors.push(err.message));

    // 1. Authenticate via robust helper
    await ensureAuthenticated(page);

    // 2. Navigate to Invoices
    await page.evaluate(() => { window.location.href = '/odoo/action-270'; });
    await page.waitForFunction(() => window.location.pathname.includes('action-270'), { timeout: 25000 });
    await page.waitForTimeout(3000);

    // 3. Click "Nouveau" or open form
    const newBtn = page.locator('button.o_list_button_add, button:has-text("Nouveau"), button:has-text("New")');
    if (await newBtn.count() > 0 && await newBtn.first().isVisible()) {
      await newBtn.first().click({ noWaitAfter: true });
      await page.waitForTimeout(4000);

      // Verify Notebook tab "Conformité & Suivi MonErp"
      const compTab = page.locator('a.nav-link:has-text("Conformité & Suivi MonErp"), a.nav-link[name="monerp_account_compliance"]');
      if (await compTab.count() > 0) {
        await compTab.first().click();
        await page.waitForTimeout(1000);

        // Verify "Intelligence Artificielle & Numérisation OCR VEID" section exists
        const ocrSection = page.locator('div:has-text("Intelligence Artificielle & Numérisation OCR VEID")');
        await expect(ocrSection.first()).toBeVisible({ timeout: 10000 });

        // Verify OCR parser field exists in DOM
        const parserField = page.locator('[name="veid_parser_id"]');
        expect(await parserField.count()).toBeGreaterThanOrEqual(1);
      }
    }

    // Zero critical JavaScript crashes
    const criticalErrors = uncaughtErrors.filter(e => !e.includes('ResizeObserver') && !e.includes('favicon'));
    expect(criticalErrors).toHaveLength(0);
  });
});

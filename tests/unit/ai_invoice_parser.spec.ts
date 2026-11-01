import { describe, it, expect } from 'vitest';

/**
 * Pure TypeScript replica of the VEID AI Invoice Heuristic & Parsing Engine logic
 */
export function parseInvoiceTextMock(text: string) {
  const res: {
    partner_name: string;
    partner_vat: string;
    invoice_ref: string;
    invoice_date: string | null;
    due_date: string | null;
    currency_code: string;
    amount_untaxed: number;
    amount_tax: number;
    amount_total: number;
    lines: Array<{ name: string; quantity: number; price_unit: number; price_subtotal: number }>;
    confidence: number;
  } = {
    partner_name: '',
    partner_vat: '',
    invoice_ref: '',
    invoice_date: null,
    due_date: null,
    currency_code: 'XOF',
    amount_untaxed: 0.0,
    amount_tax: 0.0,
    amount_total: 0.0,
    lines: [],
    confidence: 0.0,
  };

  if (!text) return res;

  let confidencePoints = 0;
  const totalPossible = 6;

  // 1. Ref
  const refMatch = text.match(/(?:Facture|Invoice|FAC|INV)[\s#N°o.:\-]+([A-Z0-9\-\/]{3,25})/i);
  if (refMatch) {
    res.invoice_ref = refMatch[1].trim();
    confidencePoints++;
  }

  // 2. VAT / NIF
  const vatMatch = text.match(/(?:NIF|IFU|RCCM|TVA|VAT)[\s:]*([A-Z0-9\-\.]{6,25})/i);
  if (vatMatch) {
    res.partner_vat = vatMatch[1].trim();
    confidencePoints++;
  }

  // 3. Date
  const dateMatch = text.match(/(?:Date(?:\s+de\s+facture)?|Emis\s+le)[\s:]*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})/i);
  if (dateMatch) {
    res.invoice_date = dateMatch[1].trim();
    confidencePoints++;
  }

  // Helper clean amount
  const cleanAmount = (s: string) => {
    const cleaned = s.replace(/\s/g, '').replace(/,/g, '.');
    const val = parseFloat(cleaned);
    return isNaN(val) ? 0.0 : val;
  };

  // 4. Amount Total TTC
  const ttcMatch = text.match(/(?:Net\s+[aà]\s+payer|Total\s+TTC|Montant\s+Total|Total\s+G[eé]n[eé]ral)[\s:]*([\d\s,\.]{3,20})/i);
  if (ttcMatch) {
    const val = cleanAmount(ttcMatch[1]);
    if (val > 0) {
      res.amount_total = val;
      confidencePoints++;
    }
  }

  // 5. Amount HT
  const htMatch = text.match(/(?:Total\s+HT|Montant\s+HT|Sous-Total)[\s:]*([\d\s,\.]{3,20})/i);
  if (htMatch) {
    const val = cleanAmount(htMatch[1]);
    if (val > 0) {
      res.amount_untaxed = val;
      confidencePoints++;
    }
  }

  // 6. TVA
  const tvaMatch = text.match(/(?:TVA|Taxe|VAT)(?:\s*(?:18%|19\.25%|\(\d+%\)))?[\s:]*([\d\s,\.]{2,15})/i);
  if (tvaMatch) {
    const val = cleanAmount(tvaMatch[1]);
    if (val > 0) {
      res.amount_tax = val;
      confidencePoints++;
    }
  }

  // Arithmetics reconciliation
  if (res.amount_total > 0 && res.amount_untaxed === 0 && res.amount_tax > 0) {
    res.amount_untaxed = Math.round((res.amount_total - res.amount_tax) * 100) / 100;
  } else if (res.amount_total > 0 && res.amount_untaxed > 0 && res.amount_tax === 0) {
    res.amount_tax = Math.round((res.amount_total - res.amount_untaxed) * 100) / 100;
  }

  // Line items
  const lines = text.split('\n');
  for (const line of lines) {
    const m = line.trim().match(/^(.*?)\s{2,}(\d+(?:[.,]\d+)?)\s+([\d\s]{2,15})\s+([\d\s]{2,15})$/);
    if (m) {
      const desc = m[1].trim();
      if (!['description', 'total', 'quantite', 'prix'].some(k => desc.toLowerCase().includes(k))) {
        const qty = cleanAmount(m[2]);
        const pu = cleanAmount(m[3]);
        const sub = cleanAmount(m[4]);
        if (qty > 0 && pu > 0) {
          res.lines.push({
            name: desc,
            quantity: qty,
            price_unit: pu,
            price_subtotal: sub || qty * pu,
          });
        }
      }
    }
  }

  res.confidence = Math.min(100.0, Math.round((confidencePoints / totalPossible) * 100.0 * 10) / 10);
  return res;
}

describe('VEID Enterprise - Phase 4 AI Invoice OCR & Heuristic Parser', () => {
  it('correctly extracts Reference, NIF and SYSCOHADA Amounts from raw invoice text', () => {
    const sampleInvoice = `
      SOCIETE GENERALE DE TRAVAUX PUBLICS DU TOGO
      NIF: 10023456789
      RCCM: TG-LOM-2021-B-1423
      Facture N°: FAC-2026-BTP-089
      Date: 15/10/2026
      
      Description                   Qte   PrixUnit    Total
      Sable fin de carriere         10    45000       450000
      Gravier concasse 15/25        5     60000       300000
      
      Total HT: 750000 FCFA
      TVA 18%: 135000 FCFA
      Net a payer: 885000 FCFA
    `;

    const result = parseInvoiceTextMock(sampleInvoice);

    expect(result.invoice_ref).toBe('FAC-2026-BTP-089');
    expect(result.partner_vat).toBe('10023456789');
    expect(result.invoice_date).toBe('15/10/2026');
    expect(result.amount_untaxed).toBe(750000);
    expect(result.amount_tax).toBe(135000);
    expect(result.amount_total).toBe(885000);
    expect(result.lines).toHaveLength(2);
    expect(result.lines[0].name).toBe('Sable fin de carriere');
    expect(result.lines[0].quantity).toBe(10);
    expect(result.lines[0].price_unit).toBe(45000);
    expect(result.confidence).toBeGreaterThanOrEqual(80);
  });

  it('performs arithmetic tax reconciliation when tax line is omitted', () => {
    const invoiceNoTvaLine = `
      AGRO-SERVICES BENIN
      Facture: INV-AGRO-772
      Total HT: 1000000
      Total TTC: 1180000
    `;

    const result = parseInvoiceTextMock(invoiceNoTvaLine);
    expect(result.amount_untaxed).toBe(1000000);
    expect(result.amount_total).toBe(1180000);
    expect(result.amount_tax).toBe(180000);
  });

  it('handles empty or unparseable input gracefully with 0% confidence', () => {
    const emptyResult = parseInvoiceTextMock('');
    expect(emptyResult.confidence).toBe(0);
    expect(emptyResult.amount_total).toBe(0);
    expect(emptyResult.lines).toHaveLength(0);
  });
});

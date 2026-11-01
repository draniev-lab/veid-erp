import { describe, it, expect } from 'vitest';

export interface MobileMoneyTransaction {
  provider: 'tmoney' | 'moov' | 'wave' | 'orange' | 'mtn';
  phoneNumber: string;
  txId?: string;
  amount: number;
}

export function validateMoMoPhone(phone: string, provider: string): boolean {
  const clean = phone.replace(/\s+/g, '');
  // Togo: +228 90/91/92/93 (T-Money), +228 96/97/98/99 (Moov Flooz)
  if (provider === 'tmoney') {
    return /^(\+228|00228)?(90|91|92|93|70|71)\d{6}$/.test(clean);
  }
  if (provider === 'moov') {
    return /^(\+228|00228)?(96|97|98|99|79)\d{6}$/.test(clean);
  }
  // Generic E.164 format for Wave, Orange, MTN
  return /^\+?[1-9]\d{7,14}$/.test(clean);
}

export function calculateLatePaymentFee(residualAmount: number, daysOverdue: number): number {
  if (daysOverdue <= 0 || residualAmount <= 0) return 0;
  // Standard OHADA / VEID formula: 1.5% per 30-day period
  const fee = residualAmount * 0.015 * (daysOverdue / 30);
  return Math.round(fee * 100) / 100;
}

describe('VEID Financial Hub - Mobile Money & OHADA Logic (Vitest)', () => {
  it('validates Togolese T-Money phone numbers correctly', () => {
    expect(validateMoMoPhone('+22890123456', 'tmoney')).toBe(true);
    expect(validateMoMoPhone('91234567', 'tmoney')).toBe(true);
    expect(validateMoMoPhone('96123456', 'tmoney')).toBe(false); // Moov prefix
  });

  it('validates Moov Money Flooz phone numbers correctly', () => {
    expect(validateMoMoPhone('+22899123456', 'moov')).toBe(true);
    expect(validateMoMoPhone('98765432', 'moov')).toBe(true);
    expect(validateMoMoPhone('90123456', 'moov')).toBe(false); // T-Money prefix
  });

  it('calculates late payment penalty with 1.5% rate per 30 days', () => {
    expect(calculateLatePaymentFee(100000, 30)).toBe(1500); // 1.5% of 100k
    expect(calculateLatePaymentFee(100000, 60)).toBe(3000); // 3.0% of 100k
    expect(calculateLatePaymentFee(100000, 0)).toBe(0);
    expect(calculateLatePaymentFee(100000, -5)).toBe(0);
  });
});

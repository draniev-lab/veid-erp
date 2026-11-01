import { describe, it, expect } from 'vitest';

export interface InvoiceItem {
  type: 'inflow' | 'outflow';
  amount: number;
  dueDays: number; // positive = future days, negative = overdue
  partnerId: number;
  partnerName: string;
}

export function computeTreasuryForecastMock(items: InvoiceItem[]) {
  const inflows = { overdue: 0, d30: 0, d60: 0, d90: 0, total: 0 };
  const outflows = { overdue: 0, d30: 0, d60: 0, d90: 0, total: 0 };
  const customerMap: Record<number, { name: string; totalDue: number; overdueAmt: number; maxOverdueDays: number }> = {};

  for (const item of items) {
    const bucket = item.type === 'inflow' ? inflows : outflows;
    if (item.dueDays < 0) {
      bucket.overdue += item.amount;
    } else if (item.dueDays <= 30) {
      bucket.d30 += item.amount;
    } else if (item.dueDays <= 60) {
      bucket.d60 += item.amount;
    } else if (item.dueDays <= 90) {
      bucket.d90 += item.amount;
    }
    bucket.total += item.amount;

    if (item.type === 'inflow') {
      if (!customerMap[item.partnerId]) {
        customerMap[item.partnerId] = {
          name: item.partnerName,
          totalDue: 0,
          overdueAmt: 0,
          maxOverdueDays: 0,
        };
      }
      customerMap[item.partnerId].totalDue += item.amount;
      if (item.dueDays < 0) {
        const absOverdue = Math.abs(item.dueDays);
        customerMap[item.partnerId].overdueAmt += item.amount;
        if (absOverdue > customerMap[item.partnerId].maxOverdueDays) {
          customerMap[item.partnerId].maxOverdueDays = absOverdue;
        }
      }
    }
  }

  const net30 = inflows.d30 - outflows.d30;
  const net60 = inflows.d60 - outflows.d60;
  const net90 = inflows.d90 - outflows.d90;
  const netTotal = inflows.total - outflows.total;

  const hasShortfall = (inflows.d30 - outflows.d30 - outflows.overdue) < 0 || netTotal < 0;

  // Customer risk scoring (0-100)
  const customerRisks = Object.entries(customerMap).map(([id, c]) => {
    const ratio = c.totalDue > 0 ? (c.overdueAmt / c.totalDue) : 0;
    const score = Math.max(0, Math.min(100, Math.round(100 - (ratio * 50) - Math.min(50, c.maxOverdueDays))));
    return {
      partnerId: Number(id),
      partnerName: c.name,
      score,
      status: score >= 75 ? 'safe' : (score >= 45 ? 'warning' : 'critical'),
    };
  });

  return {
    inflows,
    outflows,
    net: { net30, net60, net90, netTotal },
    alerts: {
      hasShortfall,
      riskLevel: hasShortfall ? 'critical' : 'safe',
    },
    customerRisks,
  };
}

describe('VEID Enterprise - Phase 4 Predictive Treasury & Risk Scoring', () => {
  it('correctly calculates 30/60/90 days inflows, outflows, and net positions', () => {
    const data: InvoiceItem[] = [
      { type: 'inflow', amount: 5000000, dueDays: 15, partnerId: 1, partnerName: 'Client Alpha' },
      { type: 'inflow', amount: 3000000, dueDays: 45, partnerId: 1, partnerName: 'Client Alpha' },
      { type: 'outflow', amount: 2000000, dueDays: 10, partnerId: 2, partnerName: 'Fournisseur BTP' },
      { type: 'outflow', amount: 4000000, dueDays: 50, partnerId: 2, partnerName: 'Fournisseur BTP' },
    ];

    const forecast = computeTreasuryForecastMock(data);

    expect(forecast.inflows.d30).toBe(5000000);
    expect(forecast.inflows.d60).toBe(3000000);
    expect(forecast.outflows.d30).toBe(2000000);
    expect(forecast.net.net30).toBe(3000000);
    expect(forecast.net.net60).toBe(-1000000);
    expect(forecast.net.netTotal).toBe(2000000);
    expect(forecast.alerts.hasShortfall).toBe(false);
  });

  it('triggers cash shortfall alert when upcoming outflows exceed inflows', () => {
    const stressedData: InvoiceItem[] = [
      { type: 'inflow', amount: 1000000, dueDays: 20, partnerId: 3, partnerName: 'Client Retard' },
      { type: 'outflow', amount: 8000000, dueDays: 15, partnerId: 4, partnerName: 'Banque Echeance' },
    ];

    const forecast = computeTreasuryForecastMock(stressedData);
    expect(forecast.alerts.hasShortfall).toBe(true);
    expect(forecast.alerts.riskLevel).toBe('critical');
  });

  it('computes accurate credit default risk score based on overdue duration and ratio', () => {
    const dataWithOverdue: InvoiceItem[] = [
      // Client 5: 100% overdue by 60 days -> score should be critical
      { type: 'inflow', amount: 4000000, dueDays: -60, partnerId: 5, partnerName: 'Client Mauvais Payeur' },
      // Client 6: 0% overdue, pays on time -> score should be 100 safe
      { type: 'inflow', amount: 10000000, dueDays: 20, partnerId: 6, partnerName: 'Client Exemplaire' },
    ];

    const forecast = computeTreasuryForecastMock(dataWithOverdue);
    const badClient = forecast.customerRisks.find(c => c.partnerId === 5);
    const goodClient = forecast.customerRisks.find(c => c.partnerId === 6);

    expect(badClient?.score).toBeLessThanOrEqual(30);
    expect(badClient?.status).toBe('critical');

    expect(goodClient?.score).toBe(100);
    expect(goodClient?.status).toBe('safe');
  });
});

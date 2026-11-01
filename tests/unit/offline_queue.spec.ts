import { describe, it, expect, beforeEach } from 'vitest';

export interface OfflineReport {
  client_uuid: string;
  type: 'construction_progress' | 'harvest_weighing';
  site_id?: number;
  lot_id?: number;
  new_progress?: number;
  parcel_id?: number;
  actual_yield_tonnes?: number;
  notes?: string;
  timestamp: string;
  status: 'pending' | 'syncing' | 'synced' | 'failed';
}

export class InMemoryOfflineQueue {
  private queue: Map<string, OfflineReport> = new Map();

  enqueue(report: Omit<OfflineReport, 'client_uuid' | 'timestamp' | 'status'> & Partial<OfflineReport>): OfflineReport {
    const item: OfflineReport = {
      ...report,
      client_uuid: report.client_uuid || `offline_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
      timestamp: report.timestamp || new Date().toISOString(),
      status: 'pending',
    };
    this.queue.set(item.client_uuid, item);
    return item;
  }

  getPending(): OfflineReport[] {
    return Array.from(this.queue.values())
      .filter(i => i.status === 'pending' || i.status === 'failed')
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  }

  markSynced(client_uuid: string) {
    const item = this.queue.get(client_uuid);
    if (item) {
      item.status = 'synced';
    }
  }

  clearSynced() {
    for (const [uuid, item] of this.queue.entries()) {
      if (item.status === 'synced') {
        this.queue.delete(uuid);
      }
    }
  }

  count(): number {
    return this.getPending().length;
  }

  resolveConflictLWW(existing: OfflineReport, incoming: OfflineReport): OfflineReport {
    const timeExisting = new Date(existing.timestamp).getTime();
    const timeIncoming = new Date(incoming.timestamp).getTime();
    return timeIncoming >= timeExisting ? incoming : existing;
  }

  createSyncBatch(maxBatchSize = 50): { reports: OfflineReport[] } {
    const pending = this.getPending().slice(0, maxBatchSize);
    return { reports: pending };
  }
}

describe('VEID Field PWA - Offline Queue & Sync Engine (Vitest)', () => {
  let queue: InMemoryOfflineQueue;

  beforeEach(() => {
    queue = new InMemoryOfflineQueue();
  });

  it('enqueues BTP progress report with pending status and auto-generated UUID', () => {
    const report = queue.enqueue({
      type: 'construction_progress',
      site_id: 1,
      lot_id: 2,
      new_progress: 55.5,
      notes: 'Coulage terminé',
    });

    expect(report.client_uuid).toBeDefined();
    expect(report.status).toBe('pending');
    expect(queue.count()).toBe(1);
  });

  it('enqueues Agriculture harvest weighing and maintains FIFO order', () => {
    const btp = queue.enqueue({
      type: 'construction_progress',
      site_id: 1,
      new_progress: 30,
      timestamp: '2026-10-20T10:00:00Z',
    });

    const agro = queue.enqueue({
      type: 'harvest_weighing',
      parcel_id: 5,
      actual_yield_tonnes: 14.2,
      timestamp: '2026-10-20T09:00:00Z',
    });

    const pending = queue.getPending();
    expect(pending).toHaveLength(2);
    // 09:00 must come before 10:00
    expect(pending[0].client_uuid).toBe(agro.client_uuid);
    expect(pending[1].client_uuid).toBe(btp.client_uuid);
  });

  it('marks reports as synced and purges them from active queue', () => {
    const item = queue.enqueue({
      type: 'harvest_weighing',
      parcel_id: 3,
      actual_yield_tonnes: 5.0,
    });

    expect(queue.count()).toBe(1);
    queue.markSynced(item.client_uuid);
    expect(queue.count()).toBe(0);

    queue.clearSynced();
    expect(queue.getPending()).toHaveLength(0);
  });

  it('resolves concurrent offline edits using Last-Write-Wins (LWW)', () => {
    const reportA: OfflineReport = {
      client_uuid: 'uuid-1',
      type: 'construction_progress',
      lot_id: 2,
      new_progress: 40,
      timestamp: '2026-10-20T12:00:00Z',
      status: 'pending',
    };

    const reportB: OfflineReport = {
      client_uuid: 'uuid-1',
      type: 'construction_progress',
      lot_id: 2,
      new_progress: 50,
      timestamp: '2026-10-20T12:05:00Z',
      status: 'pending',
    };

    const resolved = queue.resolveConflictLWW(reportA, reportB);
    expect(resolved.new_progress).toBe(50);
  });

  it('packages batch correctly for /api/v1/veid/field/sync endpoint', () => {
    for (let i = 0; i < 5; i++) {
      queue.enqueue({
        type: 'construction_progress',
        site_id: i + 1,
        new_progress: (i + 1) * 10,
      });
    }

    const batch = queue.createSyncBatch(3);
    expect(batch.reports).toHaveLength(3);
    expect(batch.reports[0].site_id).toBe(1);
  });
});

import { describe, it, expect } from 'vitest';
import * as crypto from 'crypto';

export interface AuditBlock {
  sequence: number;
  res_model: string;
  res_id: number;
  action_type: 'post' | 'approve' | 'payment' | 'cancel';
  user_id: number;
  timestamp: string;
  payload: Record<string, any>;
  prev_hash: string;
  current_hash: string;
}

export function computeBlockSha256(
  prevHash: string,
  seq: number,
  model: string,
  recId: number,
  action: string,
  userId: number,
  payloadStr: string
): string {
  const raw = `${prevHash}|${seq}|${model}|${recId}|${action}|${userId}|${payloadStr}`;
  return crypto.createHash('sha256').update(raw, 'utf8').digest('hex');
}

export class BlockchainLedger {
  private chain: AuditBlock[] = [];

  appendBlock(
    model: string,
    recId: number,
    action: 'post' | 'approve' | 'payment' | 'cancel',
    userId: number,
    payload: Record<string, any>
  ): AuditBlock {
    const seq = this.chain.length + 1;
    const prevHash = this.chain.length > 0 ? this.chain[this.chain.length - 1].current_hash : '0'.repeat(64);
    const payloadStr = JSON.stringify(payload);
    const currentHash = computeBlockSha256(prevHash, seq, model, recId, action, userId, payloadStr);

    const block: AuditBlock = {
      sequence: seq,
      res_model: model,
      res_id: recId,
      action_type: action,
      user_id: userId,
      timestamp: new Date().toISOString(),
      payload,
      prev_hash: prevHash,
      current_hash: currentHash,
    };

    this.chain.push(block);
    return block;
  }

  verifyChain(): { valid: boolean; tamperedSeq?: number; message: string } {
    let expectedPrev = '0'.repeat(64);

    for (const b of this.chain) {
      if (b.prev_hash !== expectedPrev) {
        return { valid: false, tamperedSeq: b.sequence, message: `Rupture de chaîne au bloc #${b.sequence}` };
      }

      const recomputed = computeBlockSha256(
        b.prev_hash,
        b.sequence,
        b.res_model,
        b.res_id,
        b.action_type,
        b.user_id,
        JSON.stringify(b.payload)
      );

      if (recomputed !== b.current_hash) {
        return { valid: false, tamperedSeq: b.sequence, message: `Altération de données dans le bloc #${b.sequence}` };
      }

      expectedPrev = b.current_hash;
    }

    return { valid: true, message: 'Intégrité vérifiée' };
  }

  tamperPayload(seq: number, maliciousKey: string, maliciousVal: any) {
    const b = this.chain.find(block => block.sequence === seq);
    if (b) {
      b.payload[maliciousKey] = maliciousVal;
    }
  }

  getBlocks(): AuditBlock[] {
    return this.chain;
  }
}

export function evaluateApprovalTier(amount: number): 'none' | 'daf' | 'dg' {
  if (amount > 10000000) return 'dg';
  if (amount > 1000000) return 'daf';
  return 'none';
}

export function generateDuplicateInvoiceKey(partnerId: number, ref: string, amount: number): string {
  return `${partnerId}|${ref.trim().toUpperCase()}|${amount.toFixed(2)}`;
}

describe('VEID Anti-Fraud & Cryptographic Immutable Audit Ledger (Vitest)', () => {
  it('creates genesis block with 64 zeros as prev_hash and valid SHA-256', () => {
    const ledger = new BlockchainLedger();
    const block = ledger.appendBlock('account.move', 101, 'post', 1, {
      name: 'FAC-2026-001',
      amount_total: 500000,
    });

    expect(block.sequence).toBe(1);
    expect(block.prev_hash).toBe('0'.repeat(64));
    expect(block.current_hash).toHaveLength(64);
    expect(ledger.verifyChain().valid).toBe(true);
  });

  it('chains consecutive blocks cryptographically', () => {
    const ledger = new BlockchainLedger();
    const b1 = ledger.appendBlock('account.move', 101, 'post', 1, { amount: 500000 });
    const b2 = ledger.appendBlock('account.move', 102, 'approve', 2, { amount: 2500000 });
    const b3 = ledger.appendBlock('account.payment', 45, 'payment', 1, { amount: 500000 });

    expect(b2.prev_hash).toBe(b1.current_hash);
    expect(b3.prev_hash).toBe(b2.current_hash);
    expect(ledger.verifyChain().valid).toBe(true);
  });

  it('detects fraudulent post-facto database tampering and pinpoints the corrupted block', () => {
    const ledger = new BlockchainLedger();
    ledger.appendBlock('account.move', 101, 'post', 1, { amount: 500000 });
    ledger.appendBlock('account.move', 102, 'approve', 2, { amount: 1500000 });
    ledger.appendBlock('account.move', 103, 'post', 1, { amount: 350000 });

    // Simulate an attacker modifying the amount of block 2 directly in PostgreSQL
    ledger.tamperPayload(2, 'amount', 99999999);

    const verification = ledger.verifyChain();
    expect(verification.valid).toBe(false);
    expect(verification.tamperedSeq).toBe(2);
    expect(verification.message).toContain('Altération de données');
  });

  it('evaluates approval tier correctly by monetary thresholds', () => {
    expect(evaluateApprovalTier(450000)).toBe('none'); // < 1M FCFA
    expect(evaluateApprovalTier(1000000)).toBe('none');
    expect(evaluateApprovalTier(1000001)).toBe('daf');  // 1M - 10M FCFA
    expect(evaluateApprovalTier(8500000)).toBe('daf');
    expect(evaluateApprovalTier(10000000)).toBe('daf');
    expect(evaluateApprovalTier(10000001)).toBe('dg');  // > 10M FCFA
    expect(evaluateApprovalTier(45000000)).toBe('dg');
  });

  it('generates consistent duplicate detection signatures for vendor invoices', () => {
    const sig1 = generateDuplicateInvoiceKey(42, 'FAC-FOURN-9988', 1250000);
    const sig2 = generateDuplicateInvoiceKey(42, ' fac-fourn-9988 ', 1250000);
    const sigDifferent = generateDuplicateInvoiceKey(42, 'FAC-FOURN-9989', 1250000);

    expect(sig1).toBe(sig2);
    expect(sig1).not.toBe(sigDifferent);
  });
});

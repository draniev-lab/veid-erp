# Verify model and fields
ledger = env['veid.audit.hash.ledger']
print("Model veid.audit.hash.ledger loaded:", ledger._name)

move_model = env['account.move']
fields_to_check = ['veid_approval_tier', 'veid_approval_state', 'veid_is_sealed', 'veid_ledger_block_id', 'veid_duplicate_warning']
for f in fields_to_check:
    assert f in move_model._fields, f"Missing field {f} on account.move"
print("All 5 VEID anti-fraud fields present on account.move: OK")

invoice = move_model.search([('state', '=', 'draft')], limit=1)
if not invoice:
    partner = env['res.partner'].search([], limit=1)
    invoice = move_model.create({
        'move_type': 'in_invoice',
        'partner_id': partner.id,
        'ref': 'FAC-TEST-SEAL-001',
        'invoice_line_ids': [(0, 0, {'name': 'Test matériel', 'price_unit': 12000000, 'quantity': 1})],
    })

invoice._compute_veid_approval_tier()
print(f"Invoice {invoice.id} computed tier: {invoice.veid_approval_tier}")

block = ledger.seal_record(invoice, 'approve')
print("Record sealed with block sequence:", block.sequence, "Hash:", block.current_hash[:16] + "...")

integrity = ledger.verify_chain_integrity(env.company.id)
print("Blockchain integrity result:", integrity)
assert integrity.get('valid') is True, "Chain integrity must be valid"
print("ALL ODOO ORM CHECKS PASSED SUCCESSFULLY!")

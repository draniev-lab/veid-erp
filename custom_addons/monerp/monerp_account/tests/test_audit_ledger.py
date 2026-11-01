# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install', 'monerp_account')
class TestAuditLedger(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Fournisseur Matériaux Lomé BTP',
            'supplier_rank': 1,
        })
        cls.invoice_small = cls.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': cls.partner.id,
            'ref': 'FAC-LOME-001',
            'invoice_line_ids': [(0, 0, {
                'name': 'Sable et gravier',
                'price_unit': 500000,
                'quantity': 1,
            })],
        })
        cls.invoice_large = cls.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': cls.partner.id,
            'ref': 'FAC-LOME-002',
            'invoice_line_ids': [(0, 0, {
                'name': 'Centrale à béton industrielle',
                'price_unit': 25000000,
                'quantity': 1,
            })],
        })

    def test_approval_tier_computation(self):
        """ Vérifie le palier hiérarchique requis selon le montant de la facture """
        self.invoice_small._compute_veid_approval_tier()
        self.assertEqual(self.invoice_small.veid_approval_tier, 'none', "Facture de 500k doit être 'none'")

        self.invoice_large._compute_veid_approval_tier()
        self.assertEqual(self.invoice_large.veid_approval_tier, 'dg', "Facture de 25M doit requérir le visa 'dg'")

    def test_request_and_approve_tier(self):
        """ Test le cycle de demande et d'octroi de visa avec scellement SHA-256 """
        self.invoice_large.action_veid_request_approval()
        self.assertEqual(self.invoice_large.veid_approval_state, 'pending_dg')

        # Octroi du visa
        self.invoice_large.action_veid_approve_tier()
        self.assertEqual(self.invoice_large.veid_approval_state, 'approved')
        self.assertTrue(self.invoice_large.veid_is_sealed, "La facture doit être marquée comme scellée")
        self.assertTrue(self.invoice_large.veid_ledger_block_id, "Un bloc de journal doit être associé")

        block = self.invoice_large.veid_ledger_block_id
        self.assertEqual(len(block.current_hash), 64, "Le hachage doit être un SHA-256 de 64 caractères")

    def test_chain_integrity_verification(self):
        """ Vérifie l'intégrité globale de la blockchain VEID """
        # Créer plusieurs blocs
        self.env['veid.audit.hash.ledger'].seal_record(self.invoice_small, 'post')
        self.env['veid.audit.hash.ledger'].seal_record(self.invoice_large, 'approve')

        result = self.env['veid.audit.hash.ledger'].verify_chain_integrity(self.env.company.id)
        self.assertTrue(result.get('valid'), "La chaîne d'audit doit être intègre")
        self.assertGreaterEqual(result.get('total_blocks'), 2)

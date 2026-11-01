# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install', 'monerp_account')
class TestAccountMoveMoMo(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Client Test VEID Enterprise',
            'email': 'client.test@veid.africa',
        })
        cls.invoice = cls.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': cls.partner.id,
            'name': 'INV/2026/0001',
        })

    def test_payment_reference_custom(self):
        """ Test standard formatting of VEID payment reference """
        self.invoice._compute_monerp_payment_ref()
        self.assertEqual(
            self.invoice.monerp_payment_reference_custom,
            'FAC-CLI-INV-2026-0001',
            "The computed payment reference must conform to FAC-CLI-<normalized_name>"
        )

    def test_momo_confirmation_without_tx_id_fails(self):
        """ Action must raise UserError when tx_id is missing """
        self.invoice.veid_momo_provider = 'tmoney'
        self.invoice.veid_momo_phone = '+22890001122'
        self.invoice.veid_momo_tx_id = False

        with self.assertRaises(UserError):
            self.invoice.action_veid_confirm_momo_payment()

    def test_momo_confirmation_with_tx_id_succeeds(self):
        """ Action must update status to success when tx_id is provided """
        self.invoice.veid_momo_provider = 'tmoney'
        self.invoice.veid_momo_phone = '+22890001122'
        self.invoice.veid_momo_tx_id = 'TM-20261020-9988'

        self.invoice.action_veid_confirm_momo_payment()
        self.assertEqual(self.invoice.veid_momo_status, 'success')

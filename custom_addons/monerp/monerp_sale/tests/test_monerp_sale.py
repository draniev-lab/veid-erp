# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestMonerpSale(TransactionCase):

    def setUp(self):
        super(TestMonerpSale, self).setUp()
        self.partner = self.env['res.partner'].create({'name': 'Client Vente MonErp'})
        self.product = self.env['product.product'].create({
            'name': 'Produit MonErp Test',
            'type': 'consu',
            'list_price': 100.0,
        })
        self.sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 2,
                'price_unit': 100.0,
                'discount': 20.0,
            })],
        })

    def test_01_discount_approval_block(self):
        """ Vérifie le blocage automatique lors d'une remise > 15% non approuvée """
        self.assertEqual(self.sale_order.monerp_max_discount, 20.0)
        self.assertFalse(self.sale_order.monerp_discount_approved)

        with self.assertRaises(UserError):
            self.sale_order.action_confirm()

    def test_02_discount_approval_success(self):
        """ Vérifie que l'approbation débloque la confirmation et crée le compte analytique """
        self.sale_order.action_approve_monerp_discount()
        self.assertTrue(self.sale_order.monerp_discount_approved)
        self.sale_order.action_confirm()

        self.assertEqual(self.sale_order.state, 'sale')
        self.assertTrue(self.sale_order.monerp_analytic_account_id)

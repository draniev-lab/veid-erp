# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestMonerpCrm(TransactionCase):

    def setUp(self):
        super(TestMonerpCrm, self).setUp()
        self.partner = self.env['res.partner'].create({'name': 'Client Test MonErp'})
        self.lead = self.env['crm.lead'].create({
            'name': 'Opportunité Test MonErp',
            'partner_id': self.partner.id,
            'monerp_budget_estimated': 60000,
            'monerp_decision_timeline': 'immediate',
            'priority': '3',
        })

    def test_01_prospect_score_calculation(self):
        """ Vérifie le calcul automatique du score prospect (budget + timeline + priority) """
        self.assertEqual(self.lead.monerp_prospect_score, 100)

    def test_02_action_create_quotation(self):
        """ Vérifie la génération automatique du devis depuis le prospect """
        action = self.lead.action_create_monerp_quotation()
        self.assertEqual(action['res_model'], 'sale.order')
        quotation = self.env['sale.order'].browse(action['res_id'])
        self.assertEqual(quotation.partner_id, self.partner)
        self.assertEqual(quotation.monerp_delivery_priority, 'express')

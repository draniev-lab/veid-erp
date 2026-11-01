# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestMonerpCore(TransactionCase):

    def setUp(self):
        super(TestMonerpCore, self).setUp()
        self.company = self.env.company

    def test_01_monerp_company_defaults(self):
        """ Vérifie que les caractéristiques d'édition et secteur MonErp sont initialisées """
        self.assertTrue(self.company.monerp_edition)
        self.assertEqual(self.company.monerp_edition, 'professional')
        self.assertEqual(self.company.monerp_sector, 'general')

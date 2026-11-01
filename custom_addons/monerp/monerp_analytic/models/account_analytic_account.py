# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    monerp_analytic_type = fields.Selection([
        ('project', 'Projet / Contractuel'),
        ('department', 'Département Interne'),
        ('cost_center', 'Centre de Coût'),
        ('construction', 'Chantier / BTP'),
        ('farm', 'Parcelle / Exploitation'),
    ], string="Type Analytique MonErp", default='project', required=True)

    monerp_budget_allocated = fields.Monetary(
        string="Budget Analytique Alloué",
        currency_field='currency_id'
    )

    monerp_manager_id = fields.Many2one(
        'res.users',
        string="Responsable Analytique MonErp"
    )

    budget_ids = fields.One2many(
        'monerp.analytic.budget',
        'analytic_account_id',
        string="Budgets Analytiques Alloués"
    )


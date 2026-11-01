# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class MonerpAnalyticBudget(models.Model):
    _name = 'monerp.analytic.budget'
    _description = 'Budget Analytique & Suivi des Dépenses'

    name = fields.Char(string="Intitulé du Budget Analytique", required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Compte Analytique", required=True, ondelete='cascade')
    date_start = fields.Date(string="Date Début", required=True)
    date_end = fields.Date(string="Date Fin", required=True)

    budget_allocated = fields.Monetary(string="Budget Alloué", currency_field='currency_id', required=True)
    actual_spent = fields.Monetary(string="Dépenses Réelles / Engagées", currency_field='currency_id', compute='_compute_budget_metrics', store=True)
    variance_amount = fields.Monetary(string="Solde Disponible", currency_field='currency_id', compute='_compute_budget_metrics', store=True)
    budget_utilization_rate = fields.Float(string="Taux d'Utilisation (%)", compute='_compute_budget_metrics', store=True)

    status = fields.Selection([
        ('ok', 'Sous Contrôle (< 85%)'),
        ('warning', 'Alerte Seuil (> 85%)'),
        ('exceeded', 'Budget Dépassé (> 100%)'),
    ], string="Statut Budgétaire", compute='_compute_budget_metrics', store=True)

    company_id = fields.Many2one(related='analytic_account_id.company_id')
    currency_id = fields.Many2one(related='analytic_account_id.company_id.currency_id')

    @api.depends('budget_allocated', 'analytic_account_id')
    def _compute_budget_metrics(self):
        for budget in self:
            spent = 0.0
            if 'account.analytic.line' in self.env:
                lines = self.env['account.analytic.line'].search([
                    ('account_id', '=', budget.analytic_account_id.id),
                    ('amount', '<', 0)
                ])
                spent = abs(sum(lines.mapped('amount')))

            budget.actual_spent = spent
            budget.variance_amount = budget.budget_allocated - spent
            if budget.budget_allocated > 0:
                rate = round((spent / budget.budget_allocated) * 100.0, 2)
                budget.budget_utilization_rate = rate
                if rate >= 100.0:
                    budget.status = 'exceeded'
                elif rate >= 85.0:
                    budget.status = 'warning'
                else:
                    budget.status = 'ok'
            else:
                budget.budget_utilization_rate = 0.0
                budget.status = 'ok'

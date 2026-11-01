# -*- coding: utf-8 -*-

from odoo import fields, models, api


class MonerpExecutiveDashboard(models.Model):
    _name = 'monerp.executive.dashboard'
    _description = 'Tableau de Bord Exécutif MonErp'

    name = fields.Char(string="Titre du Dashboard", required=True, default="Synthèse Exécutive MonErp")
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company)
    period = fields.Selection([
        ('month', 'Mois en cours'),
        ('quarter', 'Trimestre en cours'),
        ('year', 'Année en cours'),
    ], string="Période", default='month', required=True)

    total_sales = fields.Monetary(string="CA Total Ventes (Validé)", currency_field='currency_id', compute='_compute_kpis')
    total_purchases = fields.Monetary(string="Total Achats (Confirmé)", currency_field='currency_id', compute='_compute_kpis')
    margin_estimated = fields.Monetary(string="Marge Brute Estimée", currency_field='currency_id', compute='_compute_kpis')
    pending_invoices_count = fields.Integer(string="Factures en Attente", compute='_compute_kpis')
    currency_id = fields.Many2one(related='company_id.currency_id')

    margin_percent = fields.Float(string="Taux de Marge Brute Global (%)", compute='_compute_kpis')
    overdue_invoices_amount = fields.Monetary(string="Total Encours Impayés Clients", currency_field='currency_id', compute='_compute_kpis')
    construction_sites_count = fields.Integer(string="Chantiers BTP Actifs", compute='_compute_kpis')

    @api.depends('period', 'company_id')
    def _compute_kpis(self):
        for rec in self:
            total_sales_amount = 0.0
            total_purchases_amount = 0.0
            pending_invoices_count = 0
            overdue_amount = 0.0
            sites_count = 0

            if 'sale.order' in self.env:
                sales = self.env['sale.order'].search([
                    ('company_id', '=', rec.company_id.id),
                    ('state', 'in', ['sale', 'done'])
                ])
                total_sales_amount = sum(sales.mapped('amount_untaxed'))

            if 'purchase.order' in self.env:
                purchases = self.env['purchase.order'].search([
                    ('company_id', '=', rec.company_id.id),
                    ('state', 'in', ['purchase', 'done'])
                ])
                total_purchases_amount = sum(purchases.mapped('amount_untaxed'))

            if 'account.move' in self.env:
                pending_invoices_count = self.env['account.move'].search_count([
                    ('company_id', '=', rec.company_id.id),
                    ('state', '=', 'draft'),
                    ('move_type', 'in', ['out_invoice', 'in_invoice'])
                ])
                overdue_moves = self.env['account.move'].search([
                    ('company_id', '=', rec.company_id.id),
                    ('payment_state', 'in', ['not_paid', 'partial']),
                    ('move_type', '=', 'out_invoice'),
                    ('invoice_date_due', '<', fields.Date.context_today(self))
                ])
                overdue_amount = sum(overdue_moves.mapped('amount_residual'))

            if 'monerp.construction.site' in self.env:
                sites_count = self.env['monerp.construction.site'].search_count([
                    ('company_id', '=', rec.company_id.id),
                    ('state', '=', 'in_progress')
                ])

            rec.total_sales = total_sales_amount
            rec.total_purchases = total_purchases_amount
            margin = total_sales_amount - total_purchases_amount
            rec.margin_estimated = margin
            rec.margin_percent = round((margin / total_sales_amount) * 100.0, 2) if total_sales_amount > 0 else 0.0
            rec.pending_invoices_count = pending_invoices_count
            rec.overdue_invoices_amount = overdue_amount
            rec.construction_sites_count = sites_count




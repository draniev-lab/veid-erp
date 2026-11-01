# -*- coding: utf-8 -*-

from odoo import fields, models, api


class MonerpConstructionSite(models.Model):
    _name = 'monerp.construction.site'
    _description = 'Chantier de Construction MonErp'

    name = fields.Char(string="Nom du Chantier", required=True)
    code = fields.Char(string="Référence Chantier", required=True, copy=False, default="CHANT-NEW")
    partner_id = fields.Many2one('res.partner', string="Maître d'Ouvrage / Client", required=True)
    manager_id = fields.Many2one('res.users', string="Conducteur de Travaux", required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Compte Analytique Chantier")
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company)

    state = fields.Selection([
        ('draft', 'Étude / Préparation'),
        ('in_progress', 'En Cours de Réalisation'),
        ('paused', 'Suspendu'),
        ('delivered', 'Livré / Réceptionné'),
        ('closed', 'Clôturé'),
    ], string="Statut du Chantier", default='draft', required=True)

    progress_percentage = fields.Float(string="Avancement Global (%)", default=0.0)
    budget_total = fields.Monetary(string="Budget Prévisionnel Total", currency_field='currency_id')
    cost_to_date = fields.Monetary(string="Coût Engagé à Date", currency_field='currency_id')
    margin_estimated = fields.Monetary(string="Marge Estimée", currency_field='currency_id', compute='_compute_margin', store=True)
    currency_id = fields.Many2one(related='company_id.currency_id')

    date_start = fields.Date(string="Date Démarrage Prévue")
    date_end_estimated = fields.Date(string="Date Fin Estimée")
    notes = fields.Text(string="Description / Spécifications BTP")

    monerp_retention_rate = fields.Float(
        string="Taux Retenue de Garantie (%)",
        default=5.0
    )

    monerp_retention_amount = fields.Monetary(
        string="Montant Retenue de Garantie",
        currency_field='currency_id',
        compute='_compute_retention',
        store=True
    )

    monerp_retention_release_date = fields.Date(
        string="Date Libération Garantie"
    )

    monerp_bank_guarantee_ref = fields.Char(
        string="Réf. Caution Bancaire (Substitutive)"
    )

    monerp_budget_status = fields.Selection([
        ('ok', 'Budget Maîtrisé'),
        ('warning', 'Vigilance (> 85%)'),
        ('exceeded', 'Dépassement de Budget'),
    ], string="Alerte Budgétaire BTP", compute='_compute_margin', store=True)

    progress_line_ids = fields.One2many(
        'monerp.construction.progress.line',
        'site_id',
        string="Postes de Travaux & Lots BTP"
    )

    @api.depends('budget_total', 'cost_to_date', 'monerp_retention_rate')
    def _compute_margin(self):
        for rec in self:
            rec.margin_estimated = rec.budget_total - rec.cost_to_date
            rec.monerp_retention_amount = round(rec.budget_total * (rec.monerp_retention_rate / 100.0), 2)
            if rec.budget_total > 0:
                ratio = rec.cost_to_date / rec.budget_total
                if ratio >= 1.0:
                    rec.monerp_budget_status = 'exceeded'
                elif ratio >= 0.85:
                    rec.monerp_budget_status = 'warning'
                else:
                    rec.monerp_budget_status = 'ok'
            else:
                rec.monerp_budget_status = 'ok'


class MonerpConstructionProgressLine(models.Model):
    _name = 'monerp.construction.progress.line'
    _description = 'Ligne d\'Avancement de Travaux BTP'

    site_id = fields.Many2one('monerp.construction.site', string="Chantier", required=True, ondelete='cascade')
    name = fields.Char(string="Lot / Corps d'État BTP", required=True)
    subcontractor_id = fields.Many2one('res.partner', string="Sous-Traitant Affecté")
    allocated_budget = fields.Monetary(string="Budget Alloué Lot", currency_field='currency_id')
    progress_percentage = fields.Float(string="Avancement Lot (%)", default=0.0)
    company_id = fields.Many2one(related='site_id.company_id')
    currency_id = fields.Many2one(related='site_id.currency_id')


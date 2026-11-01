# -*- coding: utf-8 -*-

from odoo import fields, models, api


class MonerpFarmParcel(models.Model):
    _name = 'monerp.farm.parcel'
    _description = 'Parcelle Agricole MonErp'

    name = fields.Char(string="Nom / Numéro de Parcelle", required=True)
    code = fields.Char(string="Identifiant Cadastral", required=True)
    area_hectares = fields.Float(string="Superficie (Ha)", required=True, default=1.0)
    crop_type = fields.Char(string="Type de Culture (ex: Céréales, Coton, Maïs)")
    harvest_season = fields.Char(string="Campagne Agricole (ex: 2026-2027)")
    notes = fields.Text(string="Observations Agricoles")
    expected_yield_tonnes = fields.Float(string="Rendement Prévisionnel (Tonnne)", default=0.0)
    actual_yield_tonnes = fields.Float(string="Rendement Réel Récolté (Tonne)", default=0.0)

    analytic_account_id = fields.Many2one('account.analytic.account', string="Compte Analytique Parcelle")
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company)

    status = fields.Selection([
        ('preparation', 'Préparation du Sol'),
        ('sowing', 'Semis / Plantation'),
        ('growing', 'Croissance / Traitement'),
        ('harvesting', 'Récolte en cours'),
        ('fallow', 'Jachère'),
    ], string="Étape de la Parcelle", default='preparation', required=True)

    treatment_ids = fields.One2many(
        'monerp.crop.treatment',
        'parcel_id',
        string="Registre Phytosanitaire & Intrants"
    )

    total_input_cost = fields.Monetary(
        string="Coût Total des Intrants",
        currency_field='currency_id',
        compute='_compute_parcel_kpis'
    )

    cost_per_hectare = fields.Monetary(
        string="Coût de Production au Ha",
        currency_field='currency_id',
        compute='_compute_parcel_kpis'
    )

    yield_variance_percent = fields.Float(
        string="Écart de Rendement (%)",
        compute='_compute_parcel_kpis'
    )

    currency_id = fields.Many2one(related='company_id.currency_id')

    @api.depends('treatment_ids.cost_total', 'area_hectares', 'expected_yield_tonnes', 'actual_yield_tonnes')
    def _compute_parcel_kpis(self):
        for parcel in self:
            total_cost = sum(parcel.treatment_ids.mapped('cost_total'))
            parcel.total_input_cost = total_cost
            parcel.cost_per_hectare = round(total_cost / parcel.area_hectares, 2) if parcel.area_hectares > 0 else 0.0

            if parcel.expected_yield_tonnes > 0:
                parcel.yield_variance_percent = round(((parcel.actual_yield_tonnes - parcel.expected_yield_tonnes) / parcel.expected_yield_tonnes) * 100.0, 2)
            else:
                parcel.yield_variance_percent = 0.0


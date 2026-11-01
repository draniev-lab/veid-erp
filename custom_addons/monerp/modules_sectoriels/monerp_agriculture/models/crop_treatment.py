# -*- coding: utf-8 -*-

from odoo import fields, models, api


class MonerpCropTreatment(models.Model):
    _name = 'monerp.crop.treatment'
    _description = 'Registre Phytosanitaire et Intrants Agricoles'

    parcel_id = fields.Many2one('monerp.farm.parcel', string="Parcelle Agricole", required=True, ondelete='cascade')
    date = fields.Date(string="Date de Traitement", default=fields.Date.context_today, required=True)
    treatment_type = fields.Selection([
        ('phytosanitary', 'Traitement Phytosanitaire (Fongicide/Insecticide)'),
        ('fertilizer', 'Fertilisation / Engrais'),
        ('seeding', 'Semis / Ensemencement'),
        ('irrigation', 'Irrigation / Arrosage'),
    ], string="Type d'Intervention", default='phytosanitary', required=True)

    product_id = fields.Many2one('product.product', string="Intrant / Produit Utilisé", required=True)
    dosage_per_ha = fields.Float(string="Dose par Hectare (Kg ou L/Ha)", default=1.0)
    total_quantity_used = fields.Float(string="Quantité Totale Utilisée", compute='_compute_total_quantity', store=True)
    operator_id = fields.Many2one('res.users', string="Intervenant / Applicateur", default=lambda self: self.env.user)
    pre_harvest_interval_days = fields.Integer(string="Délai Avant Récolte (DAR en Jours)", default=14)
    compliance_legal = fields.Boolean(string="Conforme Réglementation Bio/SANTÉ", default=True)
    cost_total = fields.Monetary(string="Coût Total Traitement", currency_field='currency_id', compute='_compute_cost', store=True)

    company_id = fields.Many2one(related='parcel_id.company_id')
    currency_id = fields.Many2one(related='parcel_id.company_id.currency_id')

    @api.depends('dosage_per_ha', 'parcel_id.area_hectares')
    def _compute_total_quantity(self):
        for rec in self:
            rec.total_quantity_used = rec.dosage_per_ha * (rec.parcel_id.area_hectares or 1.0)

    @api.depends('total_quantity_used', 'product_id')
    def _compute_cost(self):
        for rec in self:
            unit_price = getattr(rec.product_id, 'standard_price', 0.0)
            rec.cost_total = rec.total_quantity_used * unit_price

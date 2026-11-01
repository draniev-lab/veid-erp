# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    monerp_vendor_rating = fields.Selection([
        ('1', '★☆☆☆☆ - Risque élevé'),
        ('2', '★★☆☆☆ - À surveiller'),
        ('3', '★★★☆☆ - Standard'),
        ('4', '★★★★☆ - Bon fournisseur'),
        ('5', '★★★★★ - Partenaire privilégier'),
    ], string="Évaluation Fournisseur MonErp", compute='_compute_vendor_rating', store=True, readonly=False)

    monerp_delivery_lead_time_days = fields.Integer(
        string="Délai de Livraison Théorique (Jours)",
        default=5
    )

    monerp_delivery_delay_days = fields.Integer(
        string="Retard Réel de Livraison (Jours)",
        compute='_compute_delivery_delay',
        store=True
    )

    monerp_delivery_guarantee = fields.Boolean(
        string="Garantie de Délai Respecté",
        default=True
    )

    monerp_purchase_justification = fields.Text(
        string="Motif / Justification d'Achat MonErp"
    )

    monerp_penalty_amount = fields.Monetary(
        string="Pénalité de Retard Calculée",
        currency_field='currency_id',
        compute='_compute_delivery_delay',
        store=True
    )

    monerp_sla_score = fields.Float(
        string="Score SLA Fournisseur (%)",
        compute='_compute_delivery_delay',
        store=True
    )

    @api.depends('partner_id')
    def _compute_vendor_rating(self):
        for po in self:
            if not po.partner_id:
                po.monerp_vendor_rating = '3'
                continue

            # Compute rating based on historical orders
            past_orders = self.search([
                ('partner_id', '=', po.partner_id.id),
                ('state', '=', 'purchase'),
                ('id', '!=', po.id)
            ])
            if len(past_orders) > 5:
                po.monerp_vendor_rating = '5'
            elif len(past_orders) > 2:
                po.monerp_vendor_rating = '4'
            else:
                po.monerp_vendor_rating = '3'

    @api.depends('date_approve', 'date_planned')
    def _compute_delivery_delay(self):
        for po in self:
            if po.date_approve and po.date_planned:
                delta = (po.date_planned.date() - po.date_approve.date()).days
                delay = max(0, po.monerp_delivery_lead_time_days - delta)
                po.monerp_delivery_delay_days = delay
                po.monerp_penalty_amount = delay * 50.0
                po.monerp_sla_score = max(0.0, round(100.0 - (delay * 5.0), 2))
            else:
                po.monerp_delivery_delay_days = 0
                po.monerp_penalty_amount = 0.0
                po.monerp_sla_score = 100.0



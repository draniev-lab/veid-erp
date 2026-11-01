# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    monerp_prospect_score = fields.Integer(
        string="Score de Qualification MonErp",
        compute='_compute_prospect_score',
        store=True,
        help="Note sur 100 de la valeur stratégique du prospect calculée automatiquement."
    )

    monerp_decision_timeline = fields.Selection([
        ('immediate', 'Immédiat (< 1 mois)'),
        ('quarter', 'Court terme (1 à 3 mois)'),
        ('semester', 'Moyen terme (3 à 6 mois)'),
        ('long_term', 'Long terme (> 6 mois)'),
    ], string="Échéance de Décision", default='quarter')

    monerp_budget_estimated = fields.Monetary(
        string="Budget Estimé Client",
        currency_field='company_currency',
        help="Montant estimé disponible chez le prospect."
    )

    monerp_notes_commerciales = fields.Text(
        string="Remarques Stratégiques MonErp"
    )

    monerp_risk_level = fields.Selection([
        ('low', 'Faible Risque'),
        ('medium', 'Risque Moyen'),
        ('high', 'Risque Élevé (Encours / Délai)'),
    ], string="Niveau de Risque Client", compute='_compute_risk_level', store=True)

    monerp_win_probability_ai = fields.Float(
        string="Probabilité de Succès (AI MonErp %)",
        compute='_compute_prospect_score',
        store=True,
        help="Probabilité de conversion estimée par l'algorithme MonErp."
    )

    monerp_competitors = fields.Char(
        string="Concurrents Identifiés"
    )

    @api.depends('monerp_budget_estimated', 'expected_revenue', 'monerp_decision_timeline', 'priority', 'partner_id')
    def _compute_prospect_score(self):
        for lead in self:
            score = 30  # Base
            if lead.monerp_budget_estimated > 50000:
                score += 30
            elif lead.monerp_budget_estimated > 10000:
                score += 15

            if lead.monerp_decision_timeline == 'immediate':
                score += 25
            elif lead.monerp_decision_timeline == 'quarter':
                score += 15

            if lead.priority == '3':
                score += 15
            elif lead.priority == '2':
                score += 10

            final_score = min(score, 100)
            lead.monerp_prospect_score = final_score
            lead.monerp_win_probability_ai = round(final_score * 0.95, 1)

    @api.depends('monerp_decision_timeline', 'monerp_budget_estimated', 'partner_id')
    def _compute_risk_level(self):
        for lead in self:
            if lead.monerp_decision_timeline == 'long_term' or (lead.monerp_budget_estimated > 100000 and not lead.partner_id):
                lead.monerp_risk_level = 'high'
            elif lead.monerp_decision_timeline == 'semester':
                lead.monerp_risk_level = 'medium'
            else:
                lead.monerp_risk_level = 'low'

    def action_create_monerp_quotation(self):
        """ Crée automatiquement un devis MonErp pré-rempli depuis l'opportunité """
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("Veuillez d'abord attribuer un Client / Contact à ce prospect avant de générer un devis MonErp."))

        quotation_vals = {
            'partner_id': self.partner_id.id,
            'opportunity_id': self.id,
            'campaign_id': self.campaign_id.id if self.campaign_id else False,
            'medium_id': self.medium_id.id if self.medium_id else False,
            'source_id': self.source_id.id if self.source_id else False,
        }
        sale_order_model = self.env['sale.order']
        if 'monerp_commercial_conditions' in sale_order_model._fields:
            quotation_vals['monerp_commercial_conditions'] = self.monerp_notes_commerciales or ''
        if 'monerp_delivery_priority' in sale_order_model._fields:
            quotation_vals['monerp_delivery_priority'] = 'express' if self.monerp_decision_timeline == 'immediate' else 'normal'

        quotation = sale_order_model.create(quotation_vals)
        return {
            'name': _('Devis MonErp Généré'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': quotation.id,
            'view_mode': 'form',
            'target': 'current',
        }



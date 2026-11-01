# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    monerp_discount_approved = fields.Boolean(
        string="Remise Validée MonErp",
        default=False,
        help="Indique si une remise exceptionnelle a été approuvée par le responsable commercial."
    )

    monerp_max_discount = fields.Float(
        string="Remise Maximale Ligne (%)",
        compute='_compute_max_discount',
        store=True
    )

    monerp_delivery_priority = fields.Selection([
        ('normal', 'Standard (3-5 jours)'),
        ('express', 'Express (24-48h)'),
        ('urgent', 'Urgent / Immediat'),
    ], string="Priorité de Livraison MonErp", default='normal')

    monerp_commercial_conditions = fields.Text(
        string="Conditions Particulières MonErp"
    )

    monerp_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Compte Analytique MonErp",
        help="Compte analytique principal associé à cette vente."
    )

    monerp_estimated_margin_percent = fields.Float(
        string="Marge Brute Estimée (%)",
        compute='_compute_estimated_margin',
        store=True,
        help="Taux de marge brute estimé sur l'ensemble de la commande."
    )

    monerp_margin_approved = fields.Boolean(
        string="Dérogation Marge Approuvée",
        default=False
    )

    monerp_credit_risk_approved = fields.Boolean(
        string="Dérogation Encours Client Approuvée",
        default=False
    )

    @api.depends('order_line.price_subtotal', 'order_line.product_id')
    def _compute_estimated_margin(self):
        for order in self:
            total_cost = 0.0
            for line in order.order_line:
                cost = getattr(line.product_id, 'standard_price', 0.0)
                total_cost += line.product_uom_qty * cost
            if order.amount_untaxed > 0:
                margin = order.amount_untaxed - total_cost
                order.monerp_estimated_margin_percent = round((margin / order.amount_untaxed) * 100.0, 2)
            else:
                order.monerp_estimated_margin_percent = 0.0

    @api.depends('order_line.discount')
    def _compute_max_discount(self):
        for order in self:
            discounts = order.order_line.mapped('discount')
            order.monerp_max_discount = max(discounts) if discounts else 0.0

    def action_approve_monerp_discount(self):
        """ Valide manuellement une remise soumise à approbation """
        self.ensure_one()
        self.monerp_discount_approved = True
        self.monerp_margin_approved = True
        self.monerp_credit_risk_approved = True
        return True

    def action_confirm(self):
        """ Valide la commande et vérifie les remises, marges, encours + l'imputation analytique MonErp """
        for order in self:
            # 1. Vérification remise
            if order.monerp_max_discount > 15.0 and not order.monerp_discount_approved:
                raise UserError(_(
                    "Cette commande comporte une remise supérieure à 15%% (%.2f%%). "
                    "L'approbation du Responsable Commercial MonErp est requise avant confirmation."
                ) % order.monerp_max_discount)

            # 2. Protection de Marge Brute
            if order.monerp_estimated_margin_percent < 15.0 and not order.monerp_margin_approved:
                raise UserError(_(
                    "Le taux de marge brute estimé (%.2f%%) est inférieur au seuil minimal de 15%%. "
                    "Une dérogation du Responsable de Gestion MonErp est requise."
                ) % order.monerp_estimated_margin_percent)

            # 3. Vérification Encours Client & Risque Crédit
            if order.partner_id and hasattr(order.partner_id, 'credit_limit') and order.partner_id.credit_limit > 0:
                total_outstanding = getattr(order.partner_id, 'credit', 0.0) + order.amount_total
                if total_outstanding > order.partner_id.credit_limit and not order.monerp_credit_risk_approved:
                    raise UserError(_(
                        "Le plafond de crédit du client %s (Plafond: %.2f) est dépassé (Encours + Commande: %.2f). "
                        "Une approbation spéciale MonErp est requise."
                    ) % (order.partner_id.name, order.partner_id.credit_limit, total_outstanding))

            # 4. Auto-assignation d'un compte analytique MonErp si aucun n'est présent
            if not order.monerp_analytic_account_id:
                analytic = self.env['account.analytic.account'].search([
                    ('partner_id', '=', order.partner_id.id),
                    ('company_id', '=', order.company_id.id),
                ], limit=1)
                if not analytic:
                    plan = self.env['account.analytic.plan'].search([], limit=1)
                    if not plan:
                        plan = self.env['account.analytic.plan'].create({
                            'name': _("Plan Analytique MonErp"),
                        })
                    analytic_vals = {
                        'name': _("Analytique Client - %s") % order.partner_id.name,
                        'partner_id': order.partner_id.id,
                        'plan_id': plan.id,
                        'company_id': order.company_id.id,
                    }
                    if 'monerp_analytic_type' in self.env['account.analytic.account']._fields:
                        analytic_vals['monerp_analytic_type'] = 'project'
                    analytic = self.env['account.analytic.account'].create(analytic_vals)
                order.monerp_analytic_account_id = analytic.id

        return super().action_confirm()




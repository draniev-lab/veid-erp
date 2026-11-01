# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    monerp_quality_check = fields.Selection([
        ('pending', 'En attente d\'inspection'),
        ('passed', 'Conforme / Approuvé'),
        ('rejected', 'Non conforme / Rejeté'),
    ], string="Contrôle Qualité MonErp", default='pending', tracking=True)

    monerp_qc_sample_size = fields.Integer(
        string="Taille de l'Échantillon Inspecté",
        default=10
    )

    monerp_qc_critical_defects = fields.Integer(
        string="Défauts Critiques (Bloquants)",
        default=0
    )

    monerp_qc_major_defects = fields.Integer(
        string="Défauts Majeurs",
        default=0
    )

    monerp_qc_minor_defects = fields.Integer(
        string="Défauts Mineurs",
        default=0
    )

    monerp_qc_defect_rate = fields.Float(
        string="Taux de Non-Conformité (%)",
        compute='_compute_qc_defect_rate',
        store=True
    )

    monerp_driver_name = fields.Char(
        string="Nom du Chauffeur / Transporteur",
        help="Information chauffeur pour la traçabilité des livraisons"
    )

    monerp_qc_notes = fields.Text(
        string="Notes d'Inspection Qualité"
    )

    @api.depends('monerp_qc_critical_defects', 'monerp_qc_major_defects', 'monerp_qc_minor_defects', 'monerp_qc_sample_size')
    def _compute_qc_defect_rate(self):
        for picking in self:
            total_defects = (picking.monerp_qc_critical_defects * 3) + (picking.monerp_qc_major_defects * 2) + picking.monerp_qc_minor_defects
            if picking.monerp_qc_sample_size > 0:
                picking.monerp_qc_defect_rate = round((total_defects / picking.monerp_qc_sample_size) * 100.0, 2)
            else:
                picking.monerp_qc_defect_rate = 0.0

            if picking.monerp_qc_critical_defects > 0 or picking.monerp_qc_defect_rate > 5.0:
                picking.monerp_quality_check = 'rejected'

    def action_monerp_pass_qc(self):
        """ Approuve le contrôle qualité """
        for picking in self:
            if picking.monerp_qc_critical_defects > 0:
                raise UserError(_("Impossible de valider un QC ayant au moins 1 défaut critique."))
            picking.monerp_quality_check = 'passed'

    def action_monerp_reject_qc(self):
        """ Rejette le contrôle qualité """
        for picking in self:
            picking.monerp_quality_check = 'rejected'

    def button_validate(self):
        """ Bloque la validation logistique si le matériel a été rejeté par le contrôle qualité """
        for picking in self:
            if picking.monerp_quality_check == 'rejected':
                raise UserError(_(
                    "Ce mouvement de stock a été marqué comme 'Non conforme / Rejeté' lors du contrôle qualité MonErp. "
                    "Impossible de valider ce bon tant qu'il reste rejeté."
                ))
        return super().button_validate()



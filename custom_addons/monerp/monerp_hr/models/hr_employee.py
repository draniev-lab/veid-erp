# -*- coding: utf-8 -*-

from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    monerp_employee_id_code = fields.Char(
        string="Matricule RH MonErp",
        required=False,
        copy=False
    )

    monerp_expense_approval_limit = fields.Monetary(
        string="Plafond d'Approbation Dépenses",
        currency_field='currency_id',
        default=500.0
    )

    monerp_skill_level = fields.Selection([
        ('junior', 'Junior / Débutant'),
        ('confirmed', 'Confirmé / Intermédiaire'),
        ('senior', 'Senior / Expert'),
        ('lead', 'Responsable d\'équipe'),
    ], string="Niveau d'Expertise MonErp", default='confirmed')

    monerp_certification_ids = fields.One2many(
        'monerp.hr.certification',
        'employee_id',
        string="Habilitations & Certifications Sécurité"
    )

    currency_id = fields.Many2one(related='company_id.currency_id')


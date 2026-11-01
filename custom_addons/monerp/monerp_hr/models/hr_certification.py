# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class MonerpHrCertification(models.Model):
    _name = 'monerp.hr.certification'
    _description = 'Habilitation & Certification Sécurité Employé'

    employee_id = fields.Many2one('hr.employee', string="Employé", required=True, ondelete='cascade')
    name = fields.Char(string="Nom de l'Habilitation / CACES / Permis", required=True)
    certification_type = fields.Selection([
        ('safety', 'Sécurité / SST / Extincteur'),
        ('driver', 'Permis de Conduire / Poids Lourds'),
        ('electrical', 'Habilitation Électrique (HOV/B2V)'),
        ('phytosanitary', 'Certiphyto / Habilitation Chimie'),
        ('heavy_machinery', 'CACES / Engins de Chantier BTP'),
    ], string="Domaine d'Habilitation", default='safety', required=True)

    certificate_ref = fields.Char(string="Numéro de Délivrance / Certificat", required=True)
    issue_date = fields.Date(string="Date de Obtention", required=True)
    expiration_date = fields.Date(string="Date d'Expiration", required=True)
    is_expired = fields.Boolean(string="Expiré", compute='_compute_expiration', store=True)
    notes = fields.Text(string="Remarques / Organisme de Formation")

    company_id = fields.Many2one(related='employee_id.company_id')

    @api.depends('expiration_date')
    def _compute_expiration(self):
        today = fields.Date.context_today(self)
        for cert in self:
            cert.is_expired = cert.expiration_date < today if cert.expiration_date else False

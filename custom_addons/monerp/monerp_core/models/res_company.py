# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    monerp_edition = fields.Selection([
        ('standard', 'VEID Standard'),
        ('professional', 'VEID Professional'),
        ('enterprise', 'VEID Enterprise'),
    ], string="Édition VEID", default='professional', required=True)

    monerp_sector = fields.Selection([
        ('general', 'Général / Négoce'),
        ('construction', 'BTP / Construction'),
        ('agriculture', 'Agriculture'),
        ('transport', 'Transport & Logistique'),
        ('association', 'Association / Non-Profit'),
    ], string="Secteur d'Activité VEID", default='general', required=True)

    monerp_tagline = fields.Char(
        string="Slogan VEID",
        default="Solution ERP Pro & Modulaire"
    )

    # Espaces Métiers Toggles (Activation dynamique par société)
    enable_space_btp = fields.Boolean(
        string="Espace Chantiers & BTP",
        default=True,
        help="Active la gestion des chantiers BTP, des engins et des approvisionnements de matériaux."
    )

    enable_space_agri = fields.Boolean(
        string="Espace Agro-Industrie",
        default=True,
        help="Active le suivi des parcelles agricoles, des intrants et des campagnes de récolte."
    )

    enable_space_transport = fields.Boolean(
        string="Espace Flotte & Convois",
        default=True,
        help="Active la télématique de flotte, la gestion des missions de fret et le carburant."
    )

    enable_space_momo = fields.Boolean(
        string="Hub Mobile Money (T-Money, Flooz, Wave)",
        default=True,
        help="Active la passerelle d'encaissement et de décaissement Mobile Money Ouest-Africain."
    )

    enable_space_audit = fields.Boolean(
        string="Audit Ledger SHA-256 (Anti-Fraude)",
        default=True,
        help="Active l'horodatage cryptographique et le scellement immuable des écritures."
    )

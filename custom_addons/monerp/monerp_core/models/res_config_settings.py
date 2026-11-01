# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    monerp_edition = fields.Selection(
        related='company_id.monerp_edition',
        readonly=False,
        string="Édition VEID"
    )

    monerp_sector = fields.Selection(
        related='company_id.monerp_sector',
        readonly=False,
        string="Secteur d'Activité"
    )

    monerp_tagline = fields.Char(
        related='company_id.monerp_tagline',
        readonly=False,
        string="Slogan VEID"
    )

    enable_space_btp = fields.Boolean(
        related='company_id.enable_space_btp',
        readonly=False,
        string="Espace Chantiers & BTP"
    )

    enable_space_agri = fields.Boolean(
        related='company_id.enable_space_agri',
        readonly=False,
        string="Espace Agro-Industrie"
    )

    enable_space_transport = fields.Boolean(
        related='company_id.enable_space_transport',
        readonly=False,
        string="Espace Flotte & Convois"
    )

    enable_space_momo = fields.Boolean(
        related='company_id.enable_space_momo',
        readonly=False,
        string="Hub Mobile Money (T-Money, Flooz, Wave)"
    )

    enable_space_audit = fields.Boolean(
        related='company_id.enable_space_audit',
        readonly=False,
        string="Audit Ledger SHA-256 (Anti-Fraude)"
    )

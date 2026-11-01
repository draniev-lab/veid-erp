# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResPartnerL10n(models.Model):
    _inherit = 'res.partner'

    monerp_nif = fields.Char(
        string="Numéro d'Identification Fiscale (NIF/IFU)",
        copy=False,
        help="Identifiant fiscal officiel de l'entreprise auprès de l'administration des impôts."
    )

    monerp_rccm = fields.Char(
        string="Numéro RCCM / Registre du Commerce",
        copy=False
    )

    monerp_withholding_tax_rate = fields.Float(
        string="Taux Retenue à la Source / Précompte (%)",
        default=0.0,
        help="Taux de précompte ou retenue d'impôt applicable aux opérations de ce partenaire."
    )

    monerp_tax_exemption_cert = fields.Char(
        string="Attestation d'Exonération Fiscale",
        help="Référence de l'attestation légale de dispense de TVA ou précompte."
    )

    monerp_tax_exemption_expiry = fields.Date(
        string="Date d'Expiration Exonération"
    )

    monerp_fiscal_regime = fields.Selection([
        ('real', 'Régime Réel Simplifié / Normal'),
        ('synthetic', 'Régime Synthétique / Forfaitaire'),
        ('exempt', 'Exonéré / Zone Franche / ONG'),
    ], string="Régime Fiscal MonErp", default='real')

    @api.constrains('monerp_nif')
    def _check_monerp_nif_unique(self):
        for partner in self:
            if partner.monerp_nif:
                existing = self.search([
                    ('monerp_nif', '=', partner.monerp_nif),
                    ('id', '!=', partner.id),
                    ('company_id', '=', partner.company_id.id if partner.company_id else False)
                ], limit=1)
                if existing:
                    raise ValidationError(_(
                        "Le Numéro d'Identification Fiscale (NIF) '%s' est déjà attribué au partenaire '%s'."
                    ) % (partner.monerp_nif, existing.name))

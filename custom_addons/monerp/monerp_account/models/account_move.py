# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    monerp_invoice_validation_status = fields.Selection([
        ('draft', 'Brouillon'),
        ('internal_review', 'Revue Comptable Interne'),
        ('approved', 'Facture Validée'),
        ('disputed', 'Litige Client'),
    ], string="Validation Comptable MonErp", default='draft', tracking=True)

    monerp_payment_reference_custom = fields.Char(
        string="Référence Rapprochement MonErp",
        compute='_compute_monerp_payment_ref',
        store=True
    )

    monerp_compliance_notes = fields.Text(
        string="Mentions Spécifiques de Conformité"
    )

    monerp_overdue_days = fields.Integer(
        string="Jours de Retard de Paiement",
        compute='_compute_overdue_and_fees',
        store=True
    )

    monerp_late_fee_amount = fields.Monetary(
        string="Pénalité d'Impayé Calculée (1.5%)",
        currency_field='currency_id',
        compute='_compute_overdue_and_fees',
        store=True
    )

    @api.depends('invoice_date_due', 'payment_state', 'amount_residual')
    def _compute_overdue_and_fees(self):
        today = fields.Date.context_today(self)
        for move in self:
            if move.invoice_date_due and move.payment_state in ['not_paid', 'partial'] and move.invoice_date_due < today:
                overdue = (today - move.invoice_date_due).days
                move.monerp_overdue_days = max(0, overdue)
                move.monerp_late_fee_amount = round(move.amount_residual * 0.015 * (overdue / 30.0), 2)
            else:
                move.monerp_overdue_days = 0
                move.monerp_late_fee_amount = 0.0

    @api.depends('name', 'partner_id', 'move_type')
    def _compute_monerp_payment_ref(self):
        for move in self:
            if move.name and move.name != '/':
                prefix = "FAC-CLI" if move.move_type == 'out_invoice' else "FAC-FOU"
                move.monerp_payment_reference_custom = f"{prefix}-{move.name.replace('/', '-')}"
            else:
                move.monerp_payment_reference_custom = ""

    # --- Hub Mobile Money VEID ---
    veid_momo_provider = fields.Selection([
        ('tmoney', 'T-Money (TogoCom)'),
        ('moov', 'Moov Money (Flooz)'),
        ('wave', 'Wave'),
        ('orange', 'Orange Money'),
        ('mtn', 'MTN Mobile Money'),
    ], string="Opérateur Mobile Money", tracking=True)

    veid_momo_phone = fields.Char(
        string="Numéro Téléphone Mobile Money",
        tracking=True,
        help="Numéro du compte / wallet de l'émetteur ou du bénéficiaire."
    )

    veid_momo_tx_id = fields.Char(
        string="ID Transaction Opérateur",
        copy=False,
        tracking=True,
        help="Numéro de reçu ou référence de transaction délivré par l'opérateur GSM."
    )

    veid_momo_status = fields.Selection([
        ('none', 'Non initié'),
        ('pending', 'Paiement en attente'),
        ('success', 'Paiement confirmé'),
        ('failed', 'Paiement échoué'),
    ], string="Statut Mobile Money", default='none', tracking=True)

    def action_monerp_approve_invoice(self):
        """ Approuve la conformité de la facture """
        for move in self:
            move.monerp_invoice_validation_status = 'approved'

    def action_monerp_flag_dispute(self):
        """ Marque la facture en litige """
        for move in self:
            move.monerp_invoice_validation_status = 'disputed'

    def action_veid_confirm_momo_payment(self):
        """ Valide la réception du règlement Mobile Money """
        for move in self:
            if not move.veid_momo_tx_id:
                raise UserError(_("Veuillez renseigner l'ID de Transaction Opérateur avant de confirmer le paiement Mobile Money."))
            move.veid_momo_status = 'success'
            move.message_post(body=_(
                "Paiement Mobile Money confirmé avec succès via %s (Réf: %s, Tél: %s)."
            ) % (
                dict(move._fields['veid_momo_provider'].selection).get(move.veid_momo_provider, 'Mobile Money'),
                move.veid_momo_tx_id,
                move.veid_momo_phone or 'N/A'
            ))

    # --- Gouvernance Anti-Fraude & Journal Immuable VEID ---
    veid_approval_tier = fields.Selection([
        ('none', 'Validation Comptable Standard (< 1M)'),
        ('daf', 'Approbation DAF Requise (1M - 10M)'),
        ('dg', 'Approbation Direction Générale (> 10M)'),
    ], string="Niveau d'Approbation Requis", compute='_compute_veid_approval_tier', store=True)

    veid_approval_state = fields.Selection([
        ('draft', 'Non Soumis'),
        ('pending_daf', 'En attente Visa DAF'),
        ('pending_dg', 'En attente Visa DG'),
        ('approved', 'Visa Hiérarchique Accordé'),
        ('rejected', 'Rejeté par la Direction'),
    ], string="Statut d'Approbation VEID", default='draft', tracking=True)

    veid_is_sealed = fields.Boolean(
        string="Scellé dans le Journal Immuable",
        default=False,
        copy=False,
        readonly=True,
        help="Indique que l'opération a reçu son empreinte SHA-256 dans le grand livre immuable."
    )

    veid_ledger_block_id = fields.Many2one(
        'veid.audit.hash.ledger',
        string="Bloc d'Audit Cryptographique",
        copy=False,
        readonly=True
    )

    veid_duplicate_warning = fields.Char(
        string="Alerte Doublon Anti-Fraude",
        compute='_compute_duplicate_warning',
        store=False
    )

    veid_parser_id = fields.Many2one(
        'veid.ai.invoice.parser',
        string="Origine Numérisation IA (OCR)",
        readonly=True,
        copy=False
    )

    @api.depends('amount_total', 'currency_id')
    def _compute_veid_approval_tier(self):
        for move in self:
            amount = move.amount_total or 0.0
            if amount > 10000000:
                move.veid_approval_tier = 'dg'
            elif amount > 1000000:
                move.veid_approval_tier = 'daf'
            else:
                move.veid_approval_tier = 'none'

    @api.depends('ref', 'partner_id', 'amount_total', 'move_type')
    def _compute_duplicate_warning(self):
        for move in self:
            if move.move_type in ('in_invoice', 'in_refund') and move.ref and move.partner_id:
                domain = [
                    ('id', '!=', move.id or 0),
                    ('partner_id', '=', move.partner_id.id),
                    ('ref', '=', move.ref),
                    ('move_type', '=', move.move_type),
                    ('state', '!=', 'cancel'),
                ]
                dup = self.search(domain, limit=1)
                if dup:
                    move.veid_duplicate_warning = _(
                        "⚠️ SUSPICION DE DOUBLON : La facture fournisseur %s pour le même montant existe déjà sous le numéro %s !"
                    ) % (dup.ref, dup.name)
                else:
                    move.veid_duplicate_warning = False
            else:
                move.veid_duplicate_warning = False

    def action_veid_request_approval(self):
        """ Soumet la facture au palier d'approbation adéquat selon le montant """
        for move in self:
            if move.veid_approval_tier == 'dg':
                move.veid_approval_state = 'pending_dg'
                move.message_post(body=_("Facture soumise au Visa de la Direction Générale (> 10 000 000 FCFA)."))
            elif move.veid_approval_tier == 'daf':
                move.veid_approval_state = 'pending_daf'
                move.message_post(body=_("Facture soumise au Visa du Directeur Administratif et Financier (DAF)."))
            else:
                move.veid_approval_state = 'approved'
                move.message_post(body=_("Facture approuvée automatiquement (seuil standard < 1 000 000 FCFA)."))

    def action_veid_approve_tier(self):
        """ Approuve le palier hiérarchique et scelle le bloc d'audit """
        for move in self:
            move.veid_approval_state = 'approved'
            # Scellement cryptographique dans le journal d'audit immuable
            block = self.env['veid.audit.hash.ledger'].seal_record(move, 'approve')
            move.veid_ledger_block_id = block.id
            move.veid_is_sealed = True
            move.message_post(body=_(
                "Visa hiérarchique accordé par %s. Scellé cryptographiquement sous le bloc %s (Hash SHA-256: %s...)."
            ) % (self.env.user.name, block.name, block.current_hash[:16]))

    def action_veid_reject_tier(self):
        """ Rejette l'approbation de la dépense """
        for move in self:
            move.veid_approval_state = 'rejected'
            move.message_post(body=_("Facture rejetée lors du contrôle de gouvernance par %s.") % self.env.user.name)

    def _post(self, soft=True):
        """ Interdit la comptabilisation sans visa hiérarchique si montant élevé et scelle le post """
        for move in self:
            if move.veid_approval_tier in ('daf', 'dg') and move.veid_approval_state != 'approved':
                raise UserError(_(
                    "Gouvernance Anti-Fraude VEID : Cette pièce comptable d'un montant de %s %s requiert l'approbation préalable du %s."
                ) % (
                    move.amount_total,
                    move.currency_id.symbol or '',
                    'DG' if move.veid_approval_tier == 'dg' else 'DAF'
                ))

        posted = super()._post(soft=soft)

        # Scellement systématique de toute écriture comptabilisée
        for move in posted:
            if not move.veid_ledger_block_id:
                block = self.env['veid.audit.hash.ledger'].seal_record(move, 'post')
                move.veid_ledger_block_id = block.id
                move.veid_is_sealed = True

        return posted





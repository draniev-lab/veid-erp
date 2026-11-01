# -*- coding: utf-8 -*-

import hashlib
import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class VeidAuditHashLedger(models.Model):
    _name = 'veid.audit.hash.ledger'
    _description = "Journal Cryptographique d'Audit Immuable VEID (Anti-Fraude)"
    _order = 'sequence desc, id desc'

    name = fields.Char(string="Identifiant Bloc", compute='_compute_name', store=True)
    sequence = fields.Integer(string="Numéro de Bloc", required=True, readonly=True, index=True)
    res_model = fields.Char(string="Modèle Cible", required=True, readonly=True)
    res_id = fields.Integer(string="ID Enregistrement", required=True, readonly=True)
    action_type = fields.Selection([
        ('post', 'Comptabilisation'),
        ('approve', 'Approbation Hiérarchique'),
        ('payment', 'Règlement / Décaissement'),
        ('cancel', 'Annulation / Rejet'),
    ], string="Type d'Opération", required=True, readonly=True)

    user_id = fields.Many2one('res.users', string="Opérateur / Valideur", required=True, readonly=True)
    timestamp = fields.Datetime(string="Horodatage UTC Immuable", default=fields.Datetime.now, required=True, readonly=True)
    payload_data = fields.Text(string="Empreinte Données (JSON Canonique)", required=True, readonly=True)
    prev_hash = fields.Char(string="Hachage Bloc Précédent (SHA-256)", size=64, required=True, readonly=True)
    current_hash = fields.Char(string="Hachage Bloc Actuel (SHA-256)", size=64, required=True, readonly=True, index=True)
    company_id = fields.Many2one('res.company', string="Société", required=True, readonly=True, default=lambda self: self.env.company)

    @api.depends('sequence', 'action_type')
    def _compute_name(self):
        for rec in self:
            rec.name = f"BLOCK-VEID-{rec.sequence:06d}"

    @api.model
    def compute_sha256(self, prev_hash, seq, model, rec_id, action, user_id, payload_str):
        """ Calcule le hachage SHA-256 chaîné canonique """
        raw_string = f"{prev_hash}|{seq}|{model}|{rec_id}|{action}|{user_id}|{payload_str}"
        return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

    @api.model
    def seal_record(self, record, action_type, user=None, custom_payload=None):
        """
        Scelle un enregistrement dans le journal d'audit immuable avec hachage chaîné.
        Garantit l'intégrité absolue et l'impossibilité de falsification a posteriori.
        """
        company = getattr(record, 'company_id', None) or self.env.company
        user = user or self.env.user

        # 1. Récupération du dernier bloc de la chaîne pour cette société
        last_block = self.search([('company_id', '=', company.id)], order='sequence desc', limit=1)
        next_seq = (last_block.sequence + 1) if last_block else 1
        prev_hash = last_block.current_hash if last_block else ("0" * 64)

        # 2. Construction de la charge utile canonique
        if custom_payload:
            payload_dict = custom_payload
        else:
            payload_dict = {
                'id': record.id,
                'model': record._name,
                'display_name': getattr(record, 'display_name', ''),
                'amount_total': getattr(record, 'amount_total', 0.0),
                'partner_id': getattr(record.partner_id, 'id', False) if hasattr(record, 'partner_id') else False,
                'state': getattr(record, 'state', ''),
                'company_id': company.id,
            }

        payload_str = json.dumps(payload_dict, sort_keys=True, default=str)

        # 3. Calcul du nouveau hachage SHA-256
        current_hash = self.compute_sha256(
            prev_hash, next_seq, record._name, record.id, action_type, user.id, payload_str
        )

        # 4. Création immuable du bloc
        block = self.create({
            'sequence': next_seq,
            'res_model': record._name,
            'res_id': record.id,
            'action_type': action_type,
            'user_id': user.id,
            'payload_data': payload_str,
            'prev_hash': prev_hash,
            'current_hash': current_hash,
            'company_id': company.id,
        })

        return block

    @api.model
    def verify_chain_integrity(self, company_id=None):
        """
        Vérifie l'intégrité cryptographique complète de la chaîne de blocs VEID.
        Détecte immédiatement toute modification ou altération malveillante en base.
        """
        company_id = company_id or self.env.company.id
        blocks = self.search([('company_id', '=', company_id)], order='sequence asc')

        if not blocks:
            return {'valid': True, 'total_blocks': 0, 'message': 'Aucun bloc dans le journal'}

        expected_prev_hash = "0" * 64

        for block in blocks:
            # 1. Vérifier la liaison avec le bloc précédent
            if block.prev_hash != expected_prev_hash:
                return {
                    'valid': False,
                    'error_type': 'BROKEN_CHAIN',
                    'tampered_sequence': block.sequence,
                    'message': f"Rupture de chaîne détectée au bloc #{block.sequence} !",
                }

            # 2. Recalculer le hachage pour détecter toute altération du contenu
            recalculated_hash = self.compute_sha256(
                block.prev_hash,
                block.sequence,
                block.res_model,
                block.res_id,
                block.action_type,
                block.user_id.id,
                block.payload_data
            )

            if recalculated_hash != block.current_hash:
                return {
                    'valid': False,
                    'error_type': 'PAYLOAD_TAMPERED',
                    'tampered_sequence': block.sequence,
                    'message': f"Altération de données détectée dans le bloc #{block.sequence} !",
                }

            expected_prev_hash = block.current_hash

        return {
            'valid': True,
            'total_blocks': len(blocks),
            'last_hash': expected_prev_hash,
            'message': f"Intégrité vérifiée avec succès sur l'ensemble des {len(blocks)} blocs.",
        }

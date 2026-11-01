# -*- coding: utf-8 -*-

import io
import re
import json
import base64
import logging
from datetime import datetime, date

from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


class VeidAiInvoiceParser(models.Model):
    _name = 'veid.ai.invoice.parser'
    _description = 'Moteur IA de Reconnaissance & Extraction de Factures VEID'
    _order = 'create_date desc'

    name = fields.Char(string="Référence Analyse", required=True, default=lambda self: f"OCR-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    filename = fields.Char(string="Nom du Fichier")
    file_data = fields.Binary(string="Fichier Facture (PDF/Image)", attachment=True)
    raw_text = fields.Text(string="Texte Brut Extrait")
    
    # Extracted data
    partner_name = fields.Char(string="Fournisseur Détecté")
    partner_vat = fields.Char(string="NIF / IFU / RCCM Détecté")
    invoice_ref = fields.Char(string="Réf Facture Fournisseur")
    invoice_date = fields.Date(string="Date Facture")
    due_date = fields.Date(string="Date d'Échéance")
    currency_code = fields.Char(string="Devise", default="XOF")
    
    amount_untaxed = fields.Float(string="Montant HT Extrait", digits=(16, 2))
    amount_tax = fields.Float(string="Montant TVA Extrait", digits=(16, 2))
    amount_total = fields.Float(string="Montant Total TTC Extrait", digits=(16, 2))
    
    confidence_score = fields.Float(string="Indice de Confiance IA (%)", default=0.0)
    
    # Relationships
    matched_partner_id = fields.Many2one('res.partner', string="Partenaire Rapproché")
    created_move_id = fields.Many2one('account.move', string="Facture Générée", readonly=True)
    line_ids = fields.One2many('veid.ai.invoice.line', 'parser_id', string="Lignes d'Articles Extraites")
    state = fields.Selection([
        ('draft', 'Téléversé'),
        ('parsed', 'Analysé'),
        ('validated', 'Généré'),
        ('error', 'Erreur d\'Analyse')
    ], string="État", default='draft')
    error_message = fields.Text(string="Message d'Erreur")

    @api.model
    def extract_text_from_pdf_bytes(self, pdf_bytes):
        """ Extrait le texte d'un flux binaire PDF à l'aide de PyPDF2 """
        if not PyPDF2:
            _logger.warning("PyPDF2 non installé dans l'environnement Odoo")
            return ""
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            text_pages = []
            for page in reader.pages:
                text_pages.append(page.extract_text() or "")
            return "\n".join(text_pages)
        except Exception as e:
            _logger.error("Erreur lors de l'extraction PDF: %s", str(e))
            return ""

    @api.model
    def parse_invoice_text(self, text):
        """ Analyse le texte brut avec le moteur heuristique & expressions régulières multi-formats """
        res = {
            'partner_name': '',
            'partner_vat': '',
            'invoice_ref': '',
            'invoice_date': False,
            'due_date': False,
            'currency_code': 'XOF',
            'amount_untaxed': 0.0,
            'amount_tax': 0.0,
            'amount_total': 0.0,
            'lines': [],
            'confidence': 0.0,
        }
        if not text:
            return res

        confidence_points = 0
        total_possible = 6

        # 1. Numéro / Référence de Facture
        ref_patterns = [
            r'(?:Facture|Invoice|FAC|INV)[\s#N°o.:\-]+([A-Z0-9\-\/]{3,25})',
            r'R[eé]f[eé]rence[\s:]+([A-Z0-9\-\/]{3,25})',
            r'(?:N[°o]|Num[eé]ro)[\s:]+([A-Z0-9\-\/]{3,25})',
        ]
        for pat in ref_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                res['invoice_ref'] = m.group(1).strip()
                confidence_points += 1
                break

        # 2. Identifiant Fiscal (NIF, IFU, RCCM, VAT)
        vat_patterns = [
            r'(?:NIF|IFU|RCCM|TVA|VAT)[\s:]*([A-Z0-9\-\.]{6,25})',
            r'Contribuable[\s:]*([A-Z0-9\-\.]{6,25})',
        ]
        for pat in vat_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                res['partner_vat'] = m.group(1).strip()
                confidence_points += 1
                break

        # 3. Dates (Date Facture & Échéance)
        date_patterns = [
            r'(?:Date(?:\s+de\s+facture)?|Emis\s+le)[\s:]*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})',
            r'(\d{4}[/\-.]\d{2}[/\-.]\d{2})',
            r'(\d{1,2}\s+(?:janv|f[eé]vr|mars|avr|mai|juin|juil|ao[uû]t|sept|oct|nov|d[eé]c)[a-z]*\s+\d{4})'
        ]
        for pat in date_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                date_str = m.group(1).strip()
                for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d.%m.%Y', '%d/%m/%y'):
                    try:
                        res['invoice_date'] = datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
                        confidence_points += 1
                        break
                    except ValueError:
                        continue
                if res['invoice_date']:
                    break

        due_match = re.search(r'(?:[EÉ]ch[eé]ance|Due\s+date|Date\s+limite)[\s:]*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})', text, re.IGNORECASE)
        if due_match:
            d_str = due_match.group(1).strip()
            for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d.%m.%Y'):
                try:
                    res['due_date'] = datetime.strptime(d_str, fmt).strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue

        # 4. Devise
        if re.search(r'(?:FCFA|CFA|XOF)', text, re.IGNORECASE):
            res['currency_code'] = 'XOF'
        elif re.search(r'(?:EUR|€)', text):
            res['currency_code'] = 'EUR'
        elif re.search(r'(?:USD|\$)', text):
            res['currency_code'] = 'USD'

        # Helper pour nettoyer les montants
        def clean_amount(val_str):
            if not val_str:
                return 0.0
            cleaned = val_str.replace(' ', '').replace('\xa0', '').replace(',', '.')
            try:
                return float(cleaned)
            except ValueError:
                return 0.0

        # 5. Montant TTC / Net à payer
        ttc_patterns = [
            r'(?:Net\s+[aà]\s+payer|Total\s+TTC|Montant\s+Total|Total\s+G[eé]n[eé]ral|Amount\s+Due)[\s:]*([\d\s,\.]{3,20})(?:\s*(?:FCFA|CFA|XOF|EUR|USD|€|\$))?',
            r'Total\s*:[\s]*([\d\s,\.]{3,20})'
        ]
        for pat in ttc_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                val = clean_amount(m.group(1))
                if val > 0:
                    res['amount_total'] = val
                    confidence_points += 1
                    break

        # 6. Montant HT
        ht_patterns = [
            r'(?:Total\s+HT|Montant\s+HT|Sous-Total|Subtotal)[\s:]*([\d\s,\.]{3,20})',
        ]
        for pat in ht_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                val = clean_amount(m.group(1))
                if val > 0:
                    res['amount_untaxed'] = val
                    confidence_points += 1
                    break

        # 7. Montant TVA
        tva_patterns = [
            r'(?:TVA|Taxe|VAT)(?:\s*(?:18%|19\.25%|\(\d+%\)))?[\s:]*([\d\s,\.]{2,15})',
        ]
        for pat in tva_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                val = clean_amount(m.group(1))
                if val > 0:
                    res['amount_tax'] = val
                    confidence_points += 1
                    break

        # Si HT ou TVA manquant, réconciliation arithmétique
        if res['amount_total'] > 0 and res['amount_untaxed'] == 0.0 and res['amount_tax'] > 0:
            res['amount_untaxed'] = round(res['amount_total'] - res['amount_tax'], 2)
        elif res['amount_total'] > 0 and res['amount_untaxed'] > 0 and res['amount_tax'] == 0.0:
            res['amount_tax'] = round(res['amount_total'] - res['amount_untaxed'], 2)

        # 8. Extraction des lignes d'articles
        # Chercher des blocs avec Description ... Qté ... Prix Unit ... Total
        lines = []
        for line in text.splitlines():
            line_clean = line.strip()
            # Heuristique : ligne contenant description suivi d'au moins 2 espaces puis qté et prix
            line_match = re.search(r'^(.*?)\s{2,}(\d+(?:[.,]\d+)?)\s+([\d\s]{2,15})\s+([\d\s]{2,15})$', line_clean)
            if line_match:
                desc = line_match.group(1).strip()
                # Ignore les en-têtes
                if not any(k in desc.lower() for k in ['description', 'total', 'quantite', 'prix', 'montant']):
                    qty = clean_amount(line_match.group(2))
                    pu = clean_amount(line_match.group(3))
                    subtot = clean_amount(line_match.group(4))
                    if qty > 0 and pu > 0:
                        lines.append({
                            'name': desc,
                            'quantity': qty,
                            'price_unit': pu,
                            'price_subtotal': subtot or (qty * pu),
                        })
        res['lines'] = lines

        # Calcul indice de confiance (0 - 100%)
        res['confidence'] = min(100.0, round((confidence_points / total_possible) * 100.0, 1))
        return res

    def action_parse(self):
        """ Exécute l'analyse OCR et extraction sur le fichier stocké """
        for rec in self:
            text = rec.raw_text or ""
            if rec.file_data and not text:
                try:
                    pdf_bytes = base64.b64decode(rec.file_data)
                    text = self.extract_text_from_pdf_bytes(pdf_bytes)
                    rec.raw_text = text
                except Exception as e:
                    rec.state = 'error'
                    rec.error_message = f"Erreur de décodage fichier: {str(e)}"
                    continue

            if not text:
                rec.state = 'error'
                rec.error_message = "Aucun texte extractible trouvé dans le document."
                continue

            parsed = self.parse_invoice_text(text)
            
            # Recherche de rapprochement fournisseur
            partner = False
            if parsed.get('partner_vat'):
                partner = self.env['res.partner'].search([('vat', '=', parsed['partner_vat'])], limit=1)
            if not partner and parsed.get('partner_name'):
                partner = self.env['res.partner'].search([('name', 'ilike', parsed['partner_name'])], limit=1)

            rec.write({
                'invoice_ref': parsed.get('invoice_ref') or rec.invoice_ref,
                'partner_vat': parsed.get('partner_vat') or rec.partner_vat,
                'invoice_date': parsed.get('invoice_date') or fields.Date.today(),
                'due_date': parsed.get('due_date'),
                'currency_code': parsed.get('currency_code') or 'XOF',
                'amount_untaxed': parsed.get('amount_untaxed', 0.0),
                'amount_tax': parsed.get('amount_tax', 0.0),
                'amount_total': parsed.get('amount_total', 0.0),
                'confidence_score': parsed.get('confidence', 0.0),
                'matched_partner_id': partner.id if partner else False,
                'state': 'parsed',
            })

            # Recréer les lignes
            rec.line_ids.unlink()
            for l in parsed.get('lines', []):
                self.env['veid.ai.invoice.line'].create({
                    'parser_id': rec.id,
                    'name': l['name'],
                    'quantity': l['quantity'],
                    'price_unit': l['price_unit'],
                    'price_subtotal': l['price_subtotal'],
                })

    def action_generate_vendor_bill(self):
        """ Génère automatiquement une facture fournisseur draft dans le grand livre """
        self.ensure_one()
        if not self.matched_partner_id:
            # Créer ou assigner un partenaire générique si absent
            name = self.partner_name or "Fournisseur Non Renseigné (OCR)"
            partner = self.env['res.partner'].create({
                'name': name,
                'vat': self.partner_vat or False,
                'supplier_rank': 1,
            })
            self.matched_partner_id = partner.id

        invoice_lines = []
        if self.line_ids:
            for l in self.line_ids:
                invoice_lines.append((0, 0, {
                    'name': l.name,
                    'quantity': l.quantity,
                    'price_unit': l.price_unit,
                }))
        else:
            invoice_lines.append((0, 0, {
                'name': f"Facture {self.invoice_ref or 'Importée IA'}",
                'quantity': 1,
                'price_unit': self.amount_untaxed or self.amount_total or 0.0,
            }))

        move_vals = {
            'move_type': 'in_invoice',
            'partner_id': self.matched_partner_id.id,
            'ref': self.invoice_ref or f"OCR-{self.id}",
            'invoice_date': self.invoice_date or fields.Date.today(),
            'invoice_date_due': self.due_date,
            'invoice_line_ids': invoice_lines,
        }

        move = self.env['account.move'].create(move_vals)
        self.write({
            'created_move_id': move.id,
            'state': 'validated',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
            'target': 'current',
        }


class VeidAiInvoiceLine(models.Model):
    _name = 'veid.ai.invoice.line'
    _description = 'Ligne Détectée par le Moteur IA Facture'

    parser_id = fields.Many2one('veid.ai.invoice.parser', string="Analyse Parente", ondelete='cascade')
    name = fields.Char(string="Description de l'Article", required=True)
    quantity = fields.Float(string="Quantité", default=1.0)
    price_unit = fields.Float(string="Prix Unitaire", digits=(16, 2))
    price_subtotal = fields.Float(string="Total Ligne", digits=(16, 2))

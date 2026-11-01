# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class VeidAiTreasuryForecast(models.Model):
    _name = 'veid.ai.treasury.forecast'
    _description = 'Moteur Prédictif de Trésorerie & Risque Client VEID'
    _order = 'create_date desc'

    name = fields.Char(string="Titre Analyse", required=True, default=lambda self: f"Prévision Trésorerie - {fields.Date.today()}")
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', string="Devise")
    
    # Inflows (Créances Clients)
    inflow_overdue = fields.Monetary(string="Créances Échues (En Retard)", currency_field='currency_id')
    inflow_30d = fields.Monetary(string="Encaissements Prévus (0 - 30j)", currency_field='currency_id')
    inflow_60d = fields.Monetary(string="Encaissements Prévus (31 - 60j)", currency_field='currency_id')
    inflow_90d = fields.Monetary(string="Encaissements Prévus (61 - 90j)", currency_field='currency_id')
    total_inflows = fields.Monetary(string="Total Créances Attendues", currency_field='currency_id')

    # Outflows (Dettes Fournisseurs)
    outflow_overdue = fields.Monetary(string="Dettes Échues (En Retard)", currency_field='currency_id')
    outflow_30d = fields.Monetary(string="Décaissements Prévus (0 - 30j)", currency_field='currency_id')
    outflow_60d = fields.Monetary(string="Décaissements Prévus (31 - 60j)", currency_field='currency_id')
    outflow_90d = fields.Monetary(string="Décaissements Prévus (61 - 90j)", currency_field='currency_id')
    total_outflows = fields.Monetary(string="Total Dettes à Régler", currency_field='currency_id')

    # Net Projections
    net_30d = fields.Monetary(string="Solde Net Prévisionnel 30j", currency_field='currency_id')
    net_60d = fields.Monetary(string="Solde Net Prévisionnel 60j", currency_field='currency_id')
    net_90d = fields.Monetary(string="Solde Net Prévisionnel 90j", currency_field='currency_id')
    net_total = fields.Monetary(string="Position Nette Globale", currency_field='currency_id')

    # Alerts & AI Risk
    has_cash_shortfall = fields.Boolean(string="Alerte Déficit de Trésorerie")
    shortfall_bucket = fields.Char(string="Période Critique Détectée")
    ai_risk_level = fields.Selection([
        ('safe', 'Trésorerie Saine'),
        ('moderate', 'Surveillance Requise'),
        ('critical', 'Risque Élevé de Tension')
    ], string="Niveau de Risque IA", default='safe')
    
    customer_risk_json = fields.Text(string="Détail Risque Clients (JSON)")

    @api.model
    def compute_cashflow_projection(self, company_id=None, horizon_days=90):
        """ Calcule la projection analytique complète des flux de trésorerie """
        company = self.env['res.company'].browse(company_id) if company_id else self.env.company
        today = fields.Date.today()
        d30 = today + timedelta(days=30)
        d60 = today + timedelta(days=60)
        d90 = today + timedelta(days=90)

        # 1. Factures Clients Ouvertes (Inflows)
        receivables = self.env['account.move'].search([
            ('company_id', '=', company.id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
        ])

        in_overdue = 0.0
        in_30 = 0.0
        in_60 = 0.0
        in_90 = 0.0
        
        customer_exposure = {}

        for inv in receivables:
            amt = inv.amount_residual or inv.amount_total
            due = inv.invoice_date_due or inv.invoice_date or today
            
            # Risk tracking per customer
            pid = inv.partner_id.id
            if pid not in customer_exposure:
                customer_exposure[pid] = {
                    'name': inv.partner_id.name or 'Inconnu',
                    'total_due': 0.0,
                    'overdue_amt': 0.0,
                    'max_overdue_days': 0,
                }
            customer_exposure[pid]['total_due'] += amt

            if due < today:
                in_overdue += amt
                overdue_days = (today - due).days
                customer_exposure[pid]['overdue_amt'] += amt
                if overdue_days > customer_exposure[pid]['max_overdue_days']:
                    customer_exposure[pid]['max_overdue_days'] = overdue_days
            elif due <= d30:
                in_30 += amt
            elif due <= d60:
                in_60 += amt
            elif due <= d90:
                in_90 += amt

        # 2. Factures Fournisseurs Ouvertes (Outflows)
        payables = self.env['account.move'].search([
            ('company_id', '=', company.id),
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
        ])

        out_overdue = 0.0
        out_30 = 0.0
        out_60 = 0.0
        out_90 = 0.0

        for bill in payables:
            amt = bill.amount_residual or bill.amount_total
            due = bill.invoice_date_due or bill.invoice_date or today

            if due < today:
                out_overdue += amt
            elif due <= d30:
                out_30 += amt
            elif due <= d60:
                out_60 += amt
            elif due <= d90:
                out_90 += amt

        # 3. Calculs Nets
        net_30 = in_30 - out_30
        net_60 = in_60 - out_60
        net_90 = in_90 - out_90
        net_tot = (in_overdue + in_30 + in_60 + in_90) - (out_overdue + out_30 + out_60 + out_90)

        # 4. Évaluation Risque & Alertes
        shortfall = False
        shortfall_period = ""
        risk_level = 'safe'

        if (in_30 - out_30 - out_overdue) < 0:
            shortfall = True
            shortfall_period = "Court Terme (0 - 30 jours)"
            risk_level = 'critical'
        elif net_60 < 0 or net_tot < 0:
            shortfall = True
            shortfall_period = "Moyen Terme (31 - 90 jours)"
            risk_level = 'moderate'

        # 5. Calcul Score Risque Clients (0 - 100, 100 = safe)
        risk_summary = []
        for pid, data in customer_exposure.items():
            tot = data['total_due']
            ovd = data['overdue_amt']
            ratio = (ovd / tot) if tot > 0 else 0.0
            
            # Score heuristique
            score = 100 - int(ratio * 50) - min(50, data['max_overdue_days'])
            score = max(0, min(100, score))
            
            risk_summary.append({
                'partner_id': pid,
                'partner_name': data['name'],
                'total_due': round(tot, 2),
                'overdue_amt': round(ovd, 2),
                'max_overdue_days': data['max_overdue_days'],
                'reliability_score': score,
                'status': 'safe' if score >= 75 else ('warning' if score >= 45 else 'critical'),
            })

        risk_summary.sort(key=lambda x: x['reliability_score'])

        return {
            'company_id': company.id,
            'company_name': company.name,
            'currency': company.currency_id.name,
            'inflows': {
                'overdue': round(in_overdue, 2),
                'd30': round(in_30, 2),
                'd60': round(in_60, 2),
                'd90': round(in_90, 2),
                'total': round(in_overdue + in_30 + in_60 + in_90, 2),
            },
            'outflows': {
                'overdue': round(out_overdue, 2),
                'd30': round(out_30, 2),
                'd60': round(out_60, 2),
                'd90': round(out_90, 2),
                'total': round(out_overdue + out_30 + out_60 + out_90, 2),
            },
            'net': {
                'net_30d': round(net_30, 2),
                'net_60d': round(net_60, 2),
                'net_90d': round(net_90, 2),
                'net_total': round(net_tot, 2),
            },
            'alerts': {
                'has_cash_shortfall': shortfall,
                'shortfall_bucket': shortfall_period,
                'ai_risk_level': risk_level,
            },
            'customer_risk': risk_summary[:10],
        }

    def action_refresh_forecast(self):
        """ Génère ou met à jour les données persistées du modèle """
        for rec in self:
            data = self.compute_cashflow_projection(rec.company_id.id)
            rec.write({
                'inflow_overdue': data['inflows']['overdue'],
                'inflow_30d': data['inflows']['d30'],
                'inflow_60d': data['inflows']['d60'],
                'inflow_90d': data['inflows']['d90'],
                'total_inflows': data['inflows']['total'],

                'outflow_overdue': data['outflows']['overdue'],
                'outflow_30d': data['outflows']['d30'],
                'outflow_60d': data['outflows']['d60'],
                'outflow_90d': data['outflows']['d90'],
                'total_outflows': data['outflows']['total'],

                'net_30d': data['net']['net_30d'],
                'net_60d': data['net']['net_60d'],
                'net_90d': data['net']['net_90d'],
                'net_total': data['net']['net_total'],

                'has_cash_shortfall': data['alerts']['has_cash_shortfall'],
                'shortfall_bucket': data['alerts']['shortfall_bucket'],
                'ai_risk_level': data['alerts']['ai_risk_level'],
                'customer_risk_json': str(data['customer_risk']),
            })

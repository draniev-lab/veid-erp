# -*- coding: utf-8 -*-

import json
from datetime import datetime
from odoo import http, fields, _
from odoo.http import request, Response


class VeidFieldApiController(http.Controller):

    @http.route(['/field', '/field/'], type='http', auth='public', csrf=False)
    def field_app_index(self, **kwargs):
        """ Accès direct à l'application PWA Terrain déconnectée """
        return request.redirect('/monerp_core/static/field_pwa/index.html')

    @http.route('/api/v1/veid/field/bootstrap', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False)
    def field_bootstrap(self, **kwargs):
        """
        Fournit le référentiel complet pour le fonctionnement déconnecté
        de l'application PWA Terrain (Chantiers BTP, Lots et Parcelles Agricoles).
        """
        if request.httprequest.method == 'OPTIONS':
            return self._cors_response(Response(status=200))

        env = request.env(su=True)
        data = {
            'status': 'success',
            'server_time': fields.Datetime.now().isoformat(),
            'construction_sites': [],
            'farm_parcels': [],
        }

        # 1. Chantiers de Construction BTP
        if 'monerp.construction.site' in env:
            sites = env['monerp.construction.site'].search([('state', 'in', ['draft', 'in_progress'])])
            for site in sites:
                lots = []
                for line in site.progress_line_ids:
                    lots.append({
                        'id': line.id,
                        'name': line.name,
                        'progress_percentage': line.progress_percentage,
                        'allocated_budget': line.allocated_budget or 0.0,
                    })
                data['construction_sites'].append({
                    'id': site.id,
                    'name': site.name,
                    'code': site.code,
                    'state': site.state,
                    'progress_percentage': site.progress_percentage,
                    'budget_total': site.budget_total or 0.0,
                    'cost_to_date': site.cost_to_date or 0.0,
                    'lots': lots,
                })

        # 2. Parcelles Agricoles
        if 'monerp.farm.parcel' in env:
            parcels = env['monerp.farm.parcel'].search([])
            for p in parcels:
                data['farm_parcels'].append({
                    'id': p.id,
                    'name': p.name,
                    'code': p.code,
                    'area_hectares': p.area_hectares,
                    'crop_type': p.crop_type or '',
                    'status': p.status,
                    'expected_yield_tonnes': p.expected_yield_tonnes or 0.0,
                    'actual_yield_tonnes': p.actual_yield_tonnes or 0.0,
                })

        resp = Response(
            json.dumps(data, ensure_ascii=False),
            content_type='application/json; charset=utf-8',
            status=200
        )
        return self._cors_response(resp)

    @http.route('/api/v1/veid/field/sync', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False)
    def field_sync(self, **kwargs):
        """
        Point d'entrée pour la synchronisation bidirectionnelle du flux hors-ligne.
        Reçoit un lot d'opérations différées et les applique transactionnellement.
        """
        if request.httprequest.method == 'OPTIONS':
            return self._cors_response(Response(status=200))

        env = request.env(su=True)
        raw_body = request.httprequest.data
        try:
            payload = json.loads(raw_body.decode('utf-8')) if raw_body else {}
        except Exception as e:
            resp = Response(json.dumps({'status': 'error', 'message': f'Invalid JSON: {str(e)}'}), status=400, content_type='application/json')
            return self._cors_response(resp)

        reports = payload.get('reports', [])
        synced_results = []
        errors = []

        for item in reports:
            client_uuid = item.get('client_uuid')
            report_type = item.get('type')
            try:
                if report_type == 'construction_progress':
                    lot_id = item.get('lot_id')
                    site_id = item.get('site_id')
                    new_prog = float(item.get('new_progress', 0.0))
                    notes = item.get('notes', '')

                    if lot_id and 'monerp.construction.progress.line' in env:
                        lot = env['monerp.construction.progress.line'].browse(lot_id)
                        if lot.exists():
                            lot.write({'progress_percentage': new_prog})
                            if notes and hasattr(lot.site_id, 'message_post'):
                                lot.site_id.message_post(body=_(
                                    "Pointage hors-ligne PWA synchronisé sur lot '%s' : %s%% (%s)"
                                ) % (lot.name, new_prog, notes))
                    synced_results.append({'client_uuid': client_uuid, 'status': 'applied'})

                elif report_type == 'harvest_weighing':
                    parcel_id = item.get('parcel_id')
                    weight = float(item.get('actual_yield_tonnes', 0.0))
                    notes = item.get('notes', '')

                    if parcel_id and 'monerp.farm.parcel' in env:
                        parcel = env['monerp.farm.parcel'].browse(parcel_id)
                        if parcel.exists():
                            parcel.write({'actual_yield_tonnes': parcel.actual_yield_tonnes + weight})
                            if notes and hasattr(parcel, 'message_post'):
                                parcel.message_post(body=_(
                                    "Pesée récolte hors-ligne PWA enregistrée : +%s tonnes (%s)"
                                ) % (weight, notes))
                    synced_results.append({'client_uuid': client_uuid, 'status': 'applied'})

                else:
                    errors.append({'client_uuid': client_uuid, 'error': f'Type inconnu: {report_type}'})

            except Exception as item_err:
                errors.append({'client_uuid': client_uuid, 'error': str(item_err)})

        response_data = {
            'status': 'success' if not errors else 'partial',
            'synced_count': len(synced_results),
            'results': synced_results,
            'errors': errors,
            'server_time': fields.Datetime.now().isoformat(),
        }

        resp = Response(
            json.dumps(response_data, ensure_ascii=False),
            content_type='application/json; charset=utf-8',
            status=200 if not errors else 207
        )
        return self._cors_response(resp)

    def _cors_response(self, response):
        """ Ajoute les en-têtes CORS pour le bon fonctionnement PWA """
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        return response

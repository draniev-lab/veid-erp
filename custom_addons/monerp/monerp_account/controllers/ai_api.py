# -*- coding: utf-8 -*-

import json
import base64
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class VeidAiApiController(http.Controller):

    @http.route('/api/v1/veid/ai/parse-invoice', type='http', auth='public', methods=['POST'], csrf=False)
    def api_parse_invoice(self, **kwargs):
        """ Endpoint de numérisation & reconnaissance IA de factures (PDF/Texte) """
        try:
            raw_text = ""
            file_bytes = b""
            
            # 1. Vérifier si requête JSON
            if request.httprequest.is_json:
                data = request.get_json_data() or {}
                raw_text = data.get('text', '')
                b64_file = data.get('file_base64', '')
                if b64_file:
                    try:
                        file_bytes = base64.b64decode(b64_file)
                    except Exception:
                        pass
            else:
                # 2. Form-data / multipart
                raw_text = kwargs.get('text', '')
                uploaded_file = request.httprequest.files.get('file')
                if uploaded_file:
                    file_bytes = uploaded_file.read()

            parser_model = request.env['veid.ai.invoice.parser'].sudo()

            if file_bytes and not raw_text:
                raw_text = parser_model.extract_text_from_pdf_bytes(file_bytes)

            if not raw_text:
                return request.make_response(
                    json.dumps({
                        'status': 'error',
                        'message': 'Aucun contenu textuel ou fichier PDF exploitable fourni.'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            extracted = parser_model.parse_invoice_text(raw_text)

            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'data': extracted,
                }),
                headers=[('Content-Type', 'application/json')],
                status=200
            )

        except Exception as e:
            _logger.error("Exception dans /api/v1/veid/ai/parse-invoice: %s", str(e))
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/api/v1/veid/ai/treasury-forecast', type='http', auth='public', methods=['GET'], csrf=False)
    def api_treasury_forecast(self, **kwargs):
        """ Endpoint de prévision de trésorerie & analyse de risque clients à 30/60/90j """
        try:
            company_id = kwargs.get('company_id')
            if company_id:
                try:
                    company_id = int(company_id)
                except ValueError:
                    company_id = None

            forecast_model = request.env['veid.ai.treasury.forecast'].sudo()
            result = forecast_model.compute_cashflow_projection(company_id)

            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'forecast': result,
                }),
                headers=[('Content-Type', 'application/json')],
                status=200
            )

        except Exception as e:
            _logger.error("Exception dans /api/v1/veid/ai/treasury-forecast: %s", str(e))
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

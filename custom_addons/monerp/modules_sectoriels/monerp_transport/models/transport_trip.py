# -*- coding: utf-8 -*-

from odoo import fields, models, api


class MonerpTransportTrip(models.Model):
    _name = 'monerp.transport.trip'
    _description = 'Trajet de Transport MonErp'

    name = fields.Char(string="Code Ordre de Transport", required=True, default="TRIP-NEW")
    driver_id = fields.Many2one('res.partner', string="Chauffeur / Conducteur", required=True)
    vehicle_plate = fields.Char(string="Immatriculation Véhicule", required=True)
    origin_city = fields.Char(string="Ville de Départ / Origine", required=True)
    destination_city = fields.Char(string="Ville d'Arrivée / Destination", required=True)

    date_departure = fields.Datetime(string="Date / Heure Départ")
    date_arrival_estimated = fields.Datetime(string="Date / Heure Arrivée Estimée")
    date_arrival_actual = fields.Datetime(string="Date / Heure Arrivée Réelle")

    monerp_fuel_liters = fields.Float(string="Volume Carburant Consommé (Liters)", default=0.0)
    fuel_cost = fields.Monetary(string="Coût Carburant", currency_field='currency_id', default=0.0)
    toll_cost = fields.Monetary(string="Frais Péage / Route", currency_field='currency_id', default=0.0)
    distance_km = fields.Float(string="Distance Parcourue (Km)", default=0.0)
    trip_price_billed = fields.Monetary(string="Facturation Client (Prix Fret)", currency_field='currency_id', default=0.0)
    monerp_driver_cost = fields.Monetary(string="Frais & Main d'Œuvre Chauffeur", currency_field='currency_id')

    monerp_total_trip_cost = fields.Monetary(
        string="Coût de Revient Total Trajet",
        currency_field='currency_id',
        compute='_compute_cost_per_km_engine',
        store=True
    )

    monerp_cost_per_km = fields.Monetary(
        string="Coût de Revient au Km",
        currency_field='currency_id',
        compute='_compute_cost_per_km_engine',
        store=True
    )

    monerp_trip_margin = fields.Monetary(
        string="Marge Net du Trajet",
        currency_field='currency_id',
        compute='_compute_cost_per_km_engine',
        store=True
    )

    monerp_trip_margin_percent = fields.Float(
        string="Marge Trajet (%)",
        compute='_compute_cost_per_km_engine',
        store=True
    )

    monerp_fuel_consumption_l_100 = fields.Float(
        string="Consommation Moyenne (L/100km)",
        compute='_compute_cost_per_km_engine',
        store=True
    )

    @api.depends('fuel_cost', 'toll_cost', 'monerp_driver_cost', 'distance_km', 'trip_price_billed', 'monerp_fuel_liters')
    def _compute_cost_per_km_engine(self):
        for trip in self:
            total_cost = (trip.fuel_cost or 0.0) + (trip.toll_cost or 0.0) + (trip.monerp_driver_cost or 0.0)
            trip.monerp_total_trip_cost = total_cost
            trip.monerp_cost_per_km = round(total_cost / trip.distance_km, 2) if trip.distance_km > 0 else 0.0

            margin = (trip.trip_price_billed or 0.0) - total_cost
            trip.monerp_trip_margin = margin
            if trip.trip_price_billed > 0:
                trip.monerp_trip_margin_percent = round((margin / trip.trip_price_billed) * 100.0, 2)
            else:
                trip.monerp_trip_margin_percent = 0.0

            if trip.distance_km > 0 and trip.monerp_fuel_liters > 0:
                trip.monerp_fuel_consumption_l_100 = round((trip.monerp_fuel_liters / trip.distance_km) * 100.0, 1)
            else:
                trip.monerp_fuel_consumption_l_100 = 0.0


    analytic_account_id = fields.Many2one('account.analytic.account', string="Compte Analytique Trajet")
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')

    state = fields.Selection([
        ('draft', 'Planifié'),
        ('loading', 'Chargement'),
        ('in_transit', 'En Transit'),
        ('unloading', 'Déchargement'),
        ('completed', 'Terminé / Livré'),
        ('cancelled', 'Annulé'),
    ], string="Statut du Trajet", default='draft', required=True)

    notes = fields.Text(string="Remarques & Incidents de Route")

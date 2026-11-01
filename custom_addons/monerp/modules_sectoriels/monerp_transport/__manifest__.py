# -*- coding: utf-8 -*-
{
    'name': 'VEID Secteur Transport & Flotte',
    'version': '19.0.1.0.0',
    'category': 'Vertical/Transport',
    'summary': 'Gestion du transport de fret, missions et suivi de flotte VEID',
    'description': """
VEID Transport Module
=======================
Extension sectorielle verticale pour les sociétés de transport et de logistique :
- Ordres de mission et trajets de transport
- Affectation véhicule & chauffeur
- Suivi du carburant, péages et coûts de trajet
- Suivi analytique de rentabilité par camion / trajet
    """,
    'author': 'VEID Enterprise',
    'website': 'https://veid.com',
    'license': 'LGPL-3',
    'depends': [
        'monerp_core',
        'monerp_stock',
        'monerp_analytic',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/transport_trip_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
